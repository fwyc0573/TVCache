from typing import Dict, List, Optional
from tinker import SamplingClient
from tool_schema import Response
from utils.video_sandbox_client import SandboxClient
from pathlib import Path
from tinker_cookbook.completers import TokensWithLogprobs
from tinker_cookbook.renderers import Renderer
from tinker_cookbook.rl.types import Trajectory, Transition
from threading import Lock
import json
import time


class SharedToolCache:
    """Thread-safe shared cache for tool execution results across agent loops."""

    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._lock = Lock()

    def _make_key(self, function_name: str, argument: str) -> str:
        return json.dumps({"function_name": function_name, "argument": argument})

    def get(self, function_name: str, argument: str) -> Optional[str]:
        key = self._make_key(function_name, argument)
        with self._lock:
            return self._cache.get(key, None)

    def put(self, function_name: str, argument: str, result: str):
        key = self._make_key(function_name, argument)
        with self._lock:
            self._cache[key] = result

    def has(self, function_name: str, argument: str) -> bool:
        key = self._make_key(function_name, argument)
        with self._lock:
            return key in self._cache


class CachedVideoAgentLoop:

    sampler_lock: Lock = Lock()

    def __init__(self,
                 training_data_point: Dict[str, str|int],
                 sampling_client: SamplingClient,
                 num_turns: int,
                 renderer: Renderer,
                 shared_cache: SharedToolCache,
                 sandbox_base_url: str = "http://localhost:5000",
                 rollout_log_dir: str = "./rollouts"):

        self.q = training_data_point['question']
        self.answer = training_data_point['answer']

        self.messages = [{"role": "user", "content": self.q}]
        self.sampling_client = sampling_client
        self.num_turns = num_turns
        self.renderer = renderer
        self.final_answer = None
        self.invalid_parse = False
        self.shared_cache = shared_cache
        self._stats = {
            "total_calls": 0,
            "exact_hits": 0,
            "prefix_hits": 0,
            "cache_misses": 0,
            "tool_executions": 0,
            "environment_forks": 0,
            "cache_puts": 0,
        }

        # Create sandbox client
        self.sandbox_client = SandboxClient(base_url=sandbox_base_url)
        self.sandbox_id = None
        self.log_file_path = None
        self.rollout_log_dir = rollout_log_dir

    async def start_sandbox(self, sandbox_id: str):
        self.sandbox_id = sandbox_id
        rollout_log_dir = Path(self.rollout_log_dir)
        rollout_log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file_path = str(rollout_log_dir / f"{sandbox_id}.log")
        return await self.sandbox_client.start_sandbox(sandbox_id)

    async def stop_sandbox(self):
        if self.sandbox_id:
            return await self.sandbox_client.stop_sandbox(self.sandbox_id)

    def log(self, log_line: str):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(log_line)
            log_file.write('\n')

    async def run(self, sampling_params) -> Trajectory:
        """
        Run the agent loop for multiple turns.

        Args:
            sampling_params: Parameters for sampling from the model

        Returns:
            A transition-aware trajectory for Tinker RL data assembly.
        """
        transitions: list[Transition] = []

        for turn in range(self.num_turns):
            model_input = self.renderer.build_generation_prompt(self.messages)

            self.log(f'=============Starting turn {turn}=============')
            for message in self.messages:
                self.log(f'Prompt messages: {message["content"]}')

            # Sample from the model (async)
            st = time.perf_counter()
            self.log(f'Waiting for sampler to return data in rollout {self.sandbox_id}')

            sample_result = await self.sampling_client.sample_async(
                prompt=model_input,
                num_samples=1,
                sampling_params=sampling_params
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
                self.log(f'[PARSE-ERROR]: Failed to parse response as Response schema: {e}')
                self.log(f'[PARSE-ERROR]: Raw content: {parsed_message["content"]}')
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
                self._stats["total_calls"] += 1

                cached_result = self.shared_cache.get(function_name, argument)

                if cached_result is not None:
                    self._stats["exact_hits"] += 1
                    self.log(f'[CACHE-HIT]: {function_name} with {argument}')
                    tool_result = (
                        f"Result of calling {function_name} with {argument} "
                        f"as argument is {cached_result}"
                    )
                else:
                    self._stats["cache_misses"] += 1
                    self._stats["tool_executions"] += 1
                    self.log(f'[CACHE-MISS]: {function_name} with {argument}')

                    st = time.perf_counter()
                    result = await self.sandbox_client.execute(
                        function_name,
                        argument,
                    )
                    et = time.perf_counter()

                    self.log(
                        f'[TOOL-TIME]: Time taken to call {function_name} '
                        f'with {argument}: {et - st} seconds'
                    )

                    tool_value = result['result']
                    self.shared_cache.put(
                        function_name,
                        argument,
                        tool_value,
                    )
                    self._stats["cache_puts"] += 1
                    tool_result = (
                        f"Result of calling {function_name} with {argument} "
                        f"as argument is {tool_value}"
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
        return self._stats.copy()

    def get_reward(self) -> float:
        if self.invalid_parse:
            return -2

        if self.final_answer == self.answer:
            return 1

        return 0
