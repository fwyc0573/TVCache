from tvclient.tools import ToolCallEnv, ToolCall
from dataclasses import replace
from tvclient.fork.dict_bank import SimpleDictBank
from tvclient.tools.async_semantic_stateful_executor import AsyncSemanticStatefulExecutor
import uuid
from pathlib import Path
from utils.rollout_execution import RolloutLifecycleError
from utils.video_sandbox_client import SandboxClient
from typing import Dict, List, Optional
from utils.provider_rollout import ProviderRolloutResult, run_provider_turns
from tinker import SamplingClient, types, SampleResponse
from tool_schema import Response
from utils.video_sandbox_client import SandboxClient
from tinker_cookbook.completers import TokensWithLogprobs
from tinker_cookbook.renderers import Renderer
from tinker_cookbook.rl.types import Trajectory, Transition
from tinker.types.sampling_params import SamplingParams
from threading import Lock
import time
import asyncio

class VideoToolCall(ToolCall):

    def __init__(self, function_name: str = None, argument: str = ''):
        self.function_name = function_name
        self.argument = argument

    def to_dict(self) -> dict:
        return {
            "function_name": self.function_name,
            "argument": self.argument
        }

    @staticmethod
    def from_dict(data: dict) -> 'VideoToolCall':
        return VideoToolCall(
            function_name=data.get("function_name"),
            argument=data.get("argument", '')
        )
    
    def will_mutate_state(self) -> bool:
        return self.function_name == 'preprocess' or self.function_name == 'load_video_into_sandbox'


class VideoSandboxEnv(ToolCallEnv):

    def __init__(
        self,
        env_id: Optional[str] = None,
        task_name: str = "default_task",
        sandbox_base_url: str = "http://localhost:5000",
    ):

        self.task_name = task_name
        self.sandbox_base_url = sandbox_base_url
        self.sandbox_client = SandboxClient(base_url=self.sandbox_base_url)
        self.state = {}
        self.started = False
        self._stop_operation_id = uuid.uuid4().hex

        if env_id == None:
            self.env_id =  f"{self.task_name}_{uuid.uuid4().hex}"
        else:
            self.env_id = env_id
            self.sandbox_client.sandbox_id = env_id
            self.started = True


    async def stop(self, **kwargs) -> None:

        if not self.env_id:
            raise ValueError("No env_id to stop")

        operation_id = kwargs.get("operation_id")
        if operation_id is not None:
            if not isinstance(operation_id, str) or not operation_id:
                raise ValueError(
                    "operation_id must be a non-empty string"
                )
            self._stop_operation_id = operation_id

        print(f"Stopping sandbox environment with id {self.env_id}")
        result = await self.sandbox_client.stop_sandbox(
            self.env_id,
            operation_id=self._stop_operation_id,
        )
        print(f"Stopped sandbox: {result}")
        return result

    async def execute(self, tool_call: VideoToolCall, **kwargs):
        if not self.started:
            await self.sandbox_client.start_sandbox(self.env_id)
            self.started = True

        result = await self.sandbox_client.execute(tool_call.function_name, tool_call.argument)
        return result['result']

    async def fork(self, **kwargs) -> 'VideoSandboxEnv':
        if not self.started:
            await self.sandbox_client.start_sandbox(self.env_id)
        
        forked_response = await self.sandbox_client.fork()
        assert "sandbox_id" in forked_response
        forked_env = VideoSandboxEnv(
            env_id=forked_response["sandbox_id"],
            task_name=self.task_name,
            sandbox_base_url=self.sandbox_base_url,
        )

        return forked_env

    async def get_state(self, **kwargs):
        return self.state

    def get_id(self, **kwargs) -> str:
        return self.env_id

    async def test(self) -> str:
        raise NotImplementedError("Not implemented for this")

    async def hash(self) -> str:
        raise NotImplementedError("Hash not implemented")



class VideoAgentLoop:

    sampler_lock: Lock = Lock()

    def __init__(self, 
                 training_data_point: Dict[str, str|int], 
                 sampling_client: SamplingClient, 
                 num_turns: int, 
                 renderer: Renderer, 
                 sandbox_base_url: str = "http://localhost:5000",
                 tvcache_base_url: str = "http://localhost:8001",
                 rollout_log_dir: str = "./rollouts",
                 task_id: str = ""):
        
        self.q = training_data_point['question']
        self.answer = training_data_point['answer']

        self.messages = [{"role": "user", "content": self.q}]
        self.sampling_client = sampling_client
        self.num_turns = num_turns
        self.renderer = renderer
        self.final_answer = None
        self.invalid_parse = False

        # Create sandbox client
        self.log_file_path = None
        self.rollout_log_dir = rollout_log_dir
        env_kwargs = {"sandbox_base_url": sandbox_base_url}
        self.executor = AsyncSemanticStatefulExecutor(
            tool_call_class=VideoToolCall,
            tool_call_env_class=VideoSandboxEnv,
            task_id=task_id,
            tvcache_base_url=tvcache_base_url,
            env_kwargs=env_kwargs,
        )
        self.executed_tool_calls: List[VideoToolCall] = []
        self.sandbox_id = task_id

        # set fork generator for the executor
        self.fork_generator = SimpleDictBank(
            env_class=VideoSandboxEnv,
            tvcache_base_url=tvcache_base_url,
            env_kwargs=env_kwargs,
        )
        self.executor.set_fork_bank(self.fork_generator)
        self.warmup_task_ids = training_data_point.get("next_batch", None)
        self.rollout_count = training_data_point.get("rollout_count", 0)
        self.warmup_tasks: List[asyncio.Task] = []
        self._executor_closed = False
        self._fork_generator_closed = False
        self._sandbox_withdrawn = False

    async def start_sandbox(self, sandbox_id: str):
        rollout_log_dir = Path(self.rollout_log_dir)
        rollout_log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file_path = str(rollout_log_dir / f"{sandbox_id}.log")
        self.executor.set_rollout_id(sandbox_id, self.rollout_log_dir)

    async def stop_sandbox(self):
        cleanup_errors: list[BaseException] = []

        if not self._sandbox_withdrawn:
            try:
                await self.fork_generator.withdraw(
                    task_name=self.sandbox_id,
                )
            except BaseException as error:
                cleanup_errors.append(error)
            else:
                self._sandbox_withdrawn = True

        cleanup_errors.extend(await self._close_owned_resources())

        if len(cleanup_errors) == 1:
            raise cleanup_errors[0]
        if cleanup_errors:
            raise RolloutLifecycleError(None, cleanup_errors)

    async def _close_owned_resources(self) -> list[BaseException]:
        cleanup_errors: list[BaseException] = []

        if not self._executor_closed:
            try:
                await self.executor.close()
            except BaseException as error:
                cleanup_errors.append(error)
            else:
                self._executor_closed = True

        if not self._fork_generator_closed:
            try:
                await self.fork_generator.close()
            except BaseException as error:
                cleanup_errors.append(error)
            else:
                self._fork_generator_closed = True

        return cleanup_errors
    
    def log(self, log_line: str):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(log_line)
            log_file.write('\n')
    
    async def sample_response(
        self,
        model_input,
        sampling_params: SamplingParams,
    ) -> SampleResponse:
        return await self.sampling_client.sample_async(
            prompt=model_input,
            num_samples=1,
            sampling_params=sampling_params,
        )

    async def run(
        self,
        sampling_params: SamplingParams,
    ) -> Trajectory:
        result = None
        primary_error: BaseException | None = None

        try:
            result = await self._run(sampling_params)
        except BaseException as error:
            primary_error = error

        cleanup_errors: list[BaseException] = []
        try:
            await self._finish_warmup_tasks(cancel=primary_error is not None)
        except BaseException as error:
            cleanup_errors.append(error)

        cleanup_errors.extend(await self._close_owned_resources())

        if primary_error is not None:
            if cleanup_errors:
                raise RolloutLifecycleError(
                    primary_error,
                    cleanup_errors,
                ) from primary_error
            raise primary_error

        if cleanup_errors:
            if len(cleanup_errors) == 1:
                raise cleanup_errors[0]
            raise RolloutLifecycleError(None, cleanup_errors)

        assert result is not None
        return result

    async def _finish_warmup_tasks(self, *, cancel: bool) -> None:
        if cancel:
            for task in self.warmup_tasks:
                if not task.done():
                    task.cancel()

        task_results = await asyncio.gather(
            *self.warmup_tasks,
            return_exceptions=True,
        )
        warmup_errors = [
            result
            for result in task_results
            if isinstance(result, BaseException)
            and not (cancel and isinstance(result, asyncio.CancelledError))
        ]
        self.warmup_tasks.clear()

        if len(warmup_errors) == 1:
            raise warmup_errors[0]
        if warmup_errors:
            raise RolloutLifecycleError(None, warmup_errors)

    async def _run(
        self,
        sampling_params: SamplingParams,
    ) -> Trajectory:
        """
        Run the agent loop for multiple turns.

        Args:
            renderer: The chat renderer for building prompts and parsing responses
            sampling_params: Parameters for sampling from the model

        Returns:
            A transition-aware trajectory for Tinker RL data assembly.
        """
        transitions: list[Transition] = []
        if self.warmup_task_ids != None:
            for next_task_name in self.warmup_task_ids:
                warmup_task = asyncio.create_task(
                    self.fork_generator.deposit(task_name=next_task_name, rollout_count=self.rollout_count)
                )
                self.warmup_tasks.append(warmup_task)

        for turn in range(self.num_turns):
            model_input = self.renderer.build_generation_prompt(self.messages)
            prompt_tokens = model_input.to_ints()

            self.log(f'=============Starting turn {turn}=============')
            for message in self.messages:
                self.log(f'Prompt messages: {message["content"]}')

            # Sample from the model (async)
            if len(prompt_tokens) + sampling_params.max_tokens >= 32768:
                self.log(f'Breaking because of prompt length: {len(prompt_tokens) + sampling_params.max_tokens}')
                break

            st = time.perf_counter()
            self.log(f'Waiting for sampler to return data in rollour {self.sandbox_id}')


            sample_result = await self.sample_response(
                model_input,
                sampling_params,
            )

            et = time.perf_counter()
            
            self.log(f'[GEN-TIME]: Time taken to generate: {et - st} seconds')

            sampled_tokens = sample_result.sequences[0].tokens
            sampled_logprobs = sample_result.sequences[0].logprobs
            assert sampled_logprobs is not None, "Logprobs must be enabled in sampling"

            transition = Transition(
                ob=model_input,
                ac=TokensWithLogprobs(
                    tokens=list(sampled_tokens),
                    maybe_logprobs=list(sampled_logprobs),
                ),
                reward=0.0,
                episode_done=False,
            )
            transitions.append(transition)

            parsed_message, _ = self.renderer.parse_response(sampled_tokens)

            self.log(f'Parsed message {parsed_message["content"]}')

            try:
                response = Response.model_validate_json(parsed_message["content"])
            except Exception as e:
                self.invalid_parse = True
                transition.episode_done = True
                break

            self.messages.append(parsed_message)

            if response.final_answer is not None:
                self.final_answer = response.final_answer
                transition.episode_done = True
                break
            


            for action in response.actions:
                function_name = action.tool
                argument = action.inputs

                self.log(f'Calling tool {function_name} with arguments {argument}')

                st = time.perf_counter()
                tool_call = VideoToolCall(
                    function_name=function_name,
                    argument=argument,
                )
                self.executed_tool_calls.append(tool_call)

                result = await self.executor.execute(self.executed_tool_calls)
                et = time.perf_counter()

                self.log(
                    f'[TOOL-TIME]: Time taken to call {function_name} '
                    f'with {argument}: {et - st} seconds'
                )
                tool_result = (
                    f"Result of calling {function_name} with {argument} "
                    f"as argument is: {result}"
                )

                self.messages.append({"role": "tool", "content": tool_result})

            if turn == self.num_turns - 1:
                transition.episode_done = True

        final_observation = self.renderer.build_generation_prompt(self.messages)
        return Trajectory(
            transitions=transitions,
            final_ob=final_observation,
        )

    def get_stats(self) -> dict[str, int]:
        stats = self.executor.get_stats()
        fork_stats = self.fork_generator.get_stats()
        stats["environment_forks"] += fork_stats["environment_forks"]
        return stats

    async def run_provider(
        self,
        provider_client,
    ) -> ProviderRolloutResult:
        result = await run_provider_turns(
            messages=self.messages,
            num_turns=self.num_turns,
            complete=provider_client.complete,
            execute=self._execute_provider_tool,
            answer=self.answer,
            stats=self.executor.get_stats(),
        )
        self.final_answer = result.final_answer
        self.invalid_parse = result.final_answer is None
        return replace(result, stats=self.get_stats())

    async def _execute_provider_tool(self, function_name: str, argument: str):
        tool_call = VideoToolCall(
            function_name=function_name,
            argument=argument,
        )
        self.executed_tool_calls.append(tool_call)
        return await self.executor.execute(self.executed_tool_calls)

    def get_reward(self) -> float:
        if self.invalid_parse:
            return -2
        
        if self.final_answer == self.answer:
            return 1
        
        return 0
