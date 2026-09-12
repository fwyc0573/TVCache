from typing import Any, List, Sequence, Tuple, Type

from tvclient.utils.async_tvcache_client import AsyncTVCacheClient
from tvclient.tools.tool_call_env import ToolCallEnv, ToolCall
from tvclient.fork.abstract_bank import AbstractForkGenerator

import json
import logging
from pathlib import Path
import time


FORK_THRESHOLD = 0  # seconds


class ExecutorLifecycleError(RuntimeError):
    def __init__(
        self,
        primary_error: BaseException | None,
        cleanup_errors: Sequence[BaseException],
    ):
        self.primary_error = primary_error
        self.cleanup_errors = list(cleanup_errors)

        cleanup_summary = "; ".join(
            f"{type(error).__name__}: {error}"
            for error in cleanup_errors
        )
        if primary_error is None:
            message = (
                f"{len(cleanup_errors)} cleanup operation(s) failed: "
                f"{cleanup_summary}"
            )
        else:
            message = (
                f"{type(primary_error).__name__}: {primary_error}; "
                f"{len(cleanup_errors)} cleanup operation(s) failed: "
                f"{cleanup_summary}"
            )
        super().__init__(message)


def _raise_lifecycle_errors(
    primary_error: BaseException | None,
    cleanup_errors: Sequence[BaseException],
) -> None:
    if primary_error is not None:
        if cleanup_errors:
            raise ExecutorLifecycleError(
                primary_error,
                cleanup_errors,
            ) from primary_error
        raise primary_error

    if len(cleanup_errors) == 1:
        raise cleanup_errors[0]
    if cleanup_errors:
        raise ExecutorLifecycleError(None, cleanup_errors)

class TestToolCall(ToolCall):
    def __init__(self, command: str):
        self.command = command

    def to_dict(self) -> dict:
        return {"TV_CACHE_TOOL_TYPE": "TESTING TOOL"}

    @staticmethod
    def from_dict(data: dict) -> 'TestToolCall':
        return TestToolCall(command=data["command"])

    def will_mutate_state(self) -> bool:
        return False


class AsyncSemanticStatefulExecutor:
    """Executes tool calls."""

    def __init__(
        self,
        tool_call_env_class: Type[ToolCallEnv],
        tool_call_class: Type[ToolCall],
        task_id,
        tvcache_base_url: str = "http://localhost:8001",
        env_kwargs: dict[str, Any] | None = None,
    ):
        self.client = AsyncTVCacheClient(base_url=tvcache_base_url)
        self.tool_call_env_class = tool_call_env_class
        self.tool_call_class = tool_call_class
        self.env_kwargs = dict(env_kwargs or {})
        self.tool_call_env_obj = None
        self.task_name = task_id
        self.executed_commands = 0
        self.rollout_id = str(time.time())
        self.rollout_environment: ToolCallEnv = None
        self.total_calls = 0
        self.total_executions = 0
        self.exact_hits = 0
        self.prefix_hits = 0
        self.cache_misses = 0
        self.environment_forks = 0
        self.cache_puts = 0
        self.logger = logging.getLogger(__name__)
        self._file_handler: logging.FileHandler | None = None
        self.fork_generator = None
        self._pending_cleanup_environments: list[ToolCallEnv] = []

    def _create_env(
        self,
        env_id: str | None = None,
        task_name: str | None = None,
    ) -> ToolCallEnv:
        return self.tool_call_env_class(
            env_id=env_id,
            task_name=task_name or self.task_name,
            **self.env_kwargs,
        )

    def _get_bank_env(self, parent_env_id: str) -> str | None:
        if self.fork_generator is None:
            return None
        return self.fork_generator.get_forked_env(
            task_name=self.task_name,
            parent_env_id=parent_env_id,
        )

    async def _stop_temporary_environment(
        self,
        environment: ToolCallEnv,
    ) -> None:
        try:
            await environment.stop()
        except BaseException:
            if not any(
                pending is environment
                for pending in self._pending_cleanup_environments
            ):
                self._pending_cleanup_environments.append(environment)
            raise

    def get_stats(self) -> dict[str, int]:
        return {
            "total_calls": self.total_calls,
            "exact_hits": self.exact_hits,
            "prefix_hits": self.prefix_hits,
            "cache_misses": self.cache_misses,
            "tool_executions": self.total_executions,
            "environment_forks": self.environment_forks,
            "cache_puts": self.cache_puts,
        }

    async def close(self) -> None:
        cleanup_errors: list[BaseException] = []

        if self.rollout_environment is not None:
            try:
                await self.rollout_environment.stop()
            except BaseException as error:
                cleanup_errors.append(error)
            else:
                self.rollout_environment = None

        pending_cleanup_environments: list[ToolCallEnv] = []
        for environment in self._pending_cleanup_environments:
            if environment is self.rollout_environment:
                continue
            try:
                await environment.stop()
            except BaseException as error:
                cleanup_errors.append(error)
                pending_cleanup_environments.append(environment)
        self._pending_cleanup_environments = pending_cleanup_environments

        try:
            await self.client.close()
        except BaseException as error:
            cleanup_errors.append(error)

        try:
            self._close_file_handler()
        except BaseException as error:
            cleanup_errors.append(error)

        _raise_lifecycle_errors(None, cleanup_errors)

    def set_rollout_id(self, rollout_id, rollout_log_dir):
        self._close_file_handler()
        self.rollout_id = rollout_id

        self.logger = logging.getLogger(self.rollout_id)
        self.logger.setLevel(logging.DEBUG)

        log_directory = Path(rollout_log_dir)
        log_directory.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_directory / f"{rollout_id}.log"
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self._file_handler = file_handler

    def _close_file_handler(self) -> None:
        if self._file_handler is None:
            return
        self.logger.removeHandler(self._file_handler)
        self._file_handler.close()
        self._file_handler = None
    

    def set_fork_bank(self, fork_bank: AbstractForkGenerator):
        self.fork_generator = fork_bank


    def _serialize_tool_calls(self, tool_calls: List[ToolCall]) -> List[str]:
        return [json.dumps(c.to_dict()) for c in tool_calls]
    

    async def _handle_removed_envs(self, removed_envs: List[str]) -> None:
        cleanup_errors: list[BaseException] = []
        for env_id in removed_envs:
            try:
                self.logger.debug(f'Deleting The environment {env_id} of task {self.task_name}')
                env_obj = self._create_env(env_id=env_id)
                await self._stop_temporary_environment(env_obj)
            except BaseException as error:
                cleanup_errors.append(error)

        _raise_lifecycle_errors(None, cleanup_errors)


    def _get_serialized_stateful_chain(self, tool_commands: List[ToolCall]) -> List[str]:
        stateful_chain = []
        for tool_cmd in tool_commands[: -1]:
            if tool_cmd.will_mutate_state():
                stateful_chain.append(tool_cmd)
        
        stateful_chain.append(tool_commands[-1])

        serialized_stateful_chain = self._serialize_tool_calls(stateful_chain)
        return serialized_stateful_chain

    async def _maybe_put_to_cache(
        self,
        history: List[str],
        values: List[str],
        exec_times: List[float],
        env: ToolCallEnv | None,
    ) -> None:
        env_id, value, _ = await self.client.get(self.task_name, history)
        self.logger.debug(f'Got output form check in maybe_put_to_cache: {env_id}, {value}')
        
        if env is not None:
            if env_id is None:
                fst = time.perf_counter()
                to_store: ToolCallEnv | None = await env.fork()
                self.environment_forks += 1
                fet = time.perf_counter()

                primary_error: BaseException | None = None
                cleanup_errors: list[BaseException] = []
                try:
                    removed_envs = await self.client.put(
                        self.task_name,
                        history,
                        to_store.get_id(),
                        values,
                        exec_times,
                        len(history) - len(values),
                    )
                except BaseException as error:
                    primary_error = error
                    try:
                        await self._stop_temporary_environment(to_store)
                    except BaseException as cleanup_error:
                        cleanup_errors.append(cleanup_error)

                _raise_lifecycle_errors(primary_error, cleanup_errors)
                self.cache_puts += 1

                self.logger.debug(f'Stored {history} in cache after forking which took {fet - fst} seconds. Parent={env.get_id()}, child = {to_store.get_id()}')

                await self._handle_removed_envs(removed_envs)


            else:
                self.logger.debug(f'Skipping storing env in cache because there is already environment')
        
        else:
            if value is None:
                removed_envs = await self.client.put(
                    self.task_name,
                    history,
                    None,
                    values,
                    exec_times,
                    len(history) - len(values),
                )
                self.cache_puts += 1
                
                await self._handle_removed_envs(removed_envs)
            else:
                self.logger.debug(f'SKipping storing key and value in the cache')


    async def _execute_commands(self, tool_calls: List[ToolCall], start_idx: int, env: ToolCallEnv) -> Tuple[List[str], List[float], str]:
        values = []
        execution_times = []
        test_result = None

        for idx in range(start_idx, len(tool_calls)):
            
            tool_call = tool_calls[idx]
            if idx < len(tool_calls) - 1:
                if not tool_call.will_mutate_state():
                    self.logger.debug(f'[SKIPPING]: {tool_call.to_dict()}')
                    values.append('SKIP')
                    execution_times.append(-1)
                    self.executed_commands += 1
                    continue

            if isinstance(tool_call, TestToolCall):
                assert tool_call == tool_calls[-1]
                test_result = await env.test()
                self.logger.debug(f'[TEST EXEC]: Executed test tool call {self._serialize_tool_calls(tool_calls)} for rollout {self.rollout_id} with result {test_result}')

            else:
                self.executed_commands += 1
                self.total_executions += 1
                st = time.perf_counter()
                last_state = await env.execute(tool_call)
                et = time.perf_counter()
                values.append(last_state)
                execution_times.append((et - st))
                
                self.logger.debug(f'[TOOL EXEC]: Executed tool call {self._serialize_tool_calls([tool_call])} in {et - st} seconds for rollout {self.rollout_id}')

        # logger.debug(f'[TOTAL EXEC_TIME]: {sum(execution_times)} for {self.rollout_id}')
        return values, execution_times, test_result

    async def _execute_and_put(self, commands: List[ToolCall], start_idx: int, env: ToolCallEnv) -> str:
        """Executes the commands in the tool calling environment and updates the prefix tree"""
        values, execution_times, test_result = await self._execute_commands(commands, start_idx, env)

        if test_result != None:
            history = self._serialize_tool_calls(commands)
            self.logger.debug(f'Storing test result {test_result} for history: {history}')
            primary_error: BaseException | None = None
            cleanup_errors: list[BaseException] = []
            try:
                await self.client.store_test_result(
                    self.task_name,
                    history[: len(history) - 1],
                    test_result,
                )
            except BaseException as error:
                primary_error = error

            self.logger.debug(f'[ENV]: Deleting in last step for test tool call environment {env.get_id()} of task {self.task_name} for rollout {self.rollout_id}')

            try:
                await env.stop()
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
            else:
                if env is self.rollout_environment:
                    self.rollout_environment = None

            _raise_lifecycle_errors(primary_error, cleanup_errors)
        
        else:
            st = time.perf_counter()

            assert len(execution_times) == len(commands) - start_idx, f"{execution_times} and start index {start_idx}" # this is to make sure that execute is called for each command

            tool_call_time = execution_times[-1]

            if tool_call_time > (1.0) * FORK_THRESHOLD and commands[-1].will_mutate_state():
                # We need to store this environment in the prefix tree

                stateful_chain = self._get_serialized_stateful_chain(commands)
                stateful_values = [v for v in values if v != 'SKIP']
                stateful_exec_times = [t for t in execution_times if t != -1]

                if not stateful_values[-1].startswith('Failed to execute'):
                    self.logger.debug(f'[ENV]: Maybe Storing environment after long tool call of {tool_call_time} seconds for commands: {commands}')
                    await self._maybe_put_to_cache(stateful_chain, stateful_values, stateful_exec_times, env)

            else:
                stateful_chain = self._get_serialized_stateful_chain(commands)
                stateful_values = [v for v in values if v != 'SKIP']
                stateful_exec_times = [t for t in execution_times if t != -1]
                # we do not need to store this environment in the prefix tree

                if not stateful_values[-1].startswith('Failed to execute'):
                    await self._maybe_put_to_cache(stateful_chain, stateful_values, stateful_exec_times, None)

            et = time.perf_counter()
            
            self.logger.debug(f'Time taken to store value in cache: {et - st} seconds')
            # No need to wait because the env pruning happens in the background

        if test_result != None:
            return test_result
        return values[-1]
        

    async def execute(self, tool_commands: List[ToolCall]):
        """Execute a tool call chain and publish reusable state."""
        current_tool_calls = self._serialize_tool_calls(tool_commands)
        self.total_calls += 1

        stateful_serialized_chain = self._get_serialized_stateful_chain(
            tool_commands
        )

        if await self.client.exact_match(
            self.task_name,
            stateful_serialized_chain,
        ):
            self.exact_hits += 1
            cache_start = time.perf_counter()
            _, value, tool_exec_time = await self.client.get(
                self.task_name,
                stateful_serialized_chain,
            )
            cache_end = time.perf_counter()
            self.logger.debug(
                "CACHE HIT, type 1 for task id %s with tool calls %s "
                "in %s seconds and saved tool call time %s and depth %s "
                "for rollout %s",
                self.task_name,
                current_tool_calls,
                cache_end - cache_start,
                tool_exec_time,
                len(current_tool_calls),
                self.rollout_id,
            )
            return value

        env_id, prefix_tool_calls = await self.client.prefix_match(
            self.task_name,
            stateful_serialized_chain,
        )
        if prefix_tool_calls is None:
            raise RuntimeError("TVCache prefix match returned no history")

        if len(prefix_tool_calls) == len(stateful_serialized_chain):
            if env_id is None:
                raise RuntimeError(
                    "TVCache full prefix match returned no environment ID"
                )

            self.exact_hits += 1
            primary_error: BaseException | None = None
            cleanup_errors: list[BaseException] = []
            value: Any | None = None
            try:
                _, value, _ = await self.client.get(
                    self.task_name,
                    stateful_serialized_chain,
                )
            except BaseException as error:
                primary_error = error

            try:
                await self.client.unref(env_id, self.task_name)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)

            _raise_lifecycle_errors(primary_error, cleanup_errors)
            self.logger.debug(
                "CACHE HIT, type 2 after miss for: %s",
                self.rollout_id,
            )
            return value

        if env_id is None:
            self.cache_misses += 1
            self.logger.debug(
                "CACHE MISS, for task id %s need to execute tool calls: "
                "%s for rollout %s",
                self.task_name,
                current_tool_calls,
                self.rollout_id,
            )

            if self.rollout_environment is None:
                bank_env_id = self._get_bank_env(parent_env_id="root")
                if bank_env_id is not None:
                    self.logger.debug(
                        "Found Bank root environment for task %s and "
                        "rollout %s",
                        self.task_name,
                        self.rollout_id,
                    )
                    env_obj = self._create_env(env_id=bank_env_id)
                else:
                    env_obj = self._create_env()
                self.rollout_environment = env_obj
                return await self._execute_and_put(
                    tool_commands,
                    0,
                    env_obj,
                )

            return await self._execute_and_put(
                tool_commands,
                self.executed_commands,
                self.rollout_environment,
            )

        self.prefix_hits += 1
        parent_env_id = env_id
        self.logger.debug(
            "[ENV]: Found cached env: %s for rollout %s and commands: %s",
            parent_env_id,
            self.rollout_id,
            prefix_tool_calls,
        )

        if len(prefix_tool_calls) <= self.executed_commands:
            await self.client.unref(parent_env_id, self.task_name)
            if self.rollout_environment is None:
                raise RuntimeError(
                    "TVCache prefix did not advance and no rollout "
                    "environment is active"
                )
            return await self._execute_and_put(
                tool_commands,
                self.executed_commands,
                self.rollout_environment,
            )

        previous_executed_commands = self.executed_commands
        forked_env: ToolCallEnv | None = None
        start_time = time.perf_counter()
        try:
            bank_env_id = self._get_bank_env(
                parent_env_id=parent_env_id
            )
            if bank_env_id is not None:
                self.logger.debug(
                    "Found fork bank entry for %s and %s",
                    self.task_name,
                    parent_env_id,
                )
                forked_env = self._create_env(env_id=bank_env_id)
            else:
                parent_env = self._create_env(env_id=parent_env_id)
                self.logger.debug(
                    "Could not find fork bank entry for %s and %s, "
                    "forking from scratch",
                    self.task_name,
                    parent_env_id,
                )
                forked_env = await parent_env.fork()
                self.environment_forks += 1

            duration = time.perf_counter() - start_time
            self.logger.debug(
                "[ENV]: Extended environment: %s in %.2f seconds from "
                "parent: %s for rollout %s with prefix %s",
                forked_env.get_id(),
                duration,
                parent_env_id,
                self.rollout_id,
                prefix_tool_calls,
            )
        except BaseException as primary_error:
            cleanup_errors: list[BaseException] = []
            try:
                await self.client.unref(parent_env_id, self.task_name)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
            if forked_env is not None:
                try:
                    await self._stop_temporary_environment(forked_env)
                except BaseException as cleanup_error:
                    cleanup_errors.append(cleanup_error)
            _raise_lifecycle_errors(primary_error, cleanup_errors)

        assert forked_env is not None
        try:
            await self.client.unref(parent_env_id, self.task_name)
        except BaseException as primary_error:
            cleanup_errors = []
            try:
                await self._stop_temporary_environment(forked_env)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
            _raise_lifecycle_errors(primary_error, cleanup_errors)

        self.executed_commands = len(prefix_tool_calls)
        try:
            result = await self._execute_and_put(
                tool_commands,
                len(prefix_tool_calls),
                forked_env,
            )
        except BaseException as primary_error:
            self.executed_commands = previous_executed_commands
            cleanup_errors = []
            try:
                await self._stop_temporary_environment(forked_env)
            except BaseException as cleanup_error:
                cleanup_errors.append(cleanup_error)
            _raise_lifecycle_errors(primary_error, cleanup_errors)

        previous_environment = self.rollout_environment
        if (
            previous_environment is not None
            and previous_environment is not forked_env
        ):
            try:
                await previous_environment.stop()
            except BaseException as primary_error:
                cleanup_errors = []
                try:
                    await self._stop_temporary_environment(forked_env)
                except BaseException as cleanup_error:
                    cleanup_errors.append(cleanup_error)
                _raise_lifecycle_errors(primary_error, cleanup_errors)

        self.rollout_environment = forked_env

        return result


    async def test(self, tool_call_history: List[ToolCall]) -> str:
        found, value = await self.client.get_test_result(self.task_name, self._serialize_tool_calls(tool_call_history))

        if found:
            self.total_calls += 1
            self.exact_hits += 1
            self.logger.debug(f'Found test result in Cache, CACHE HIT for task id {self.task_name}')
            return value
        self.logger.debug(f'No test result in Cache, CACHE MISS for task id {self.task_name}')
        test_tool_call = TestToolCall("")
        tool_call_history.append(test_tool_call)
        return await self.execute(tool_call_history)
