from tvclient.utils.async_tvcache_client import AsyncTVCacheClient
from tvclient.tools.tool_call_env import ToolCallEnv
from typing import Any, Type, Dict, List, Sequence
import logging
from tvclient.fork.abstract_bank import AbstractForkGenerator
from threading import Lock

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ROOT_KEY = "root"


class ForkBankLifecycleError(RuntimeError):
    def __init__(
        self,
        primary_error: BaseException | None,
        cleanup_errors: Sequence[BaseException],
    ):
        self.primary_error = primary_error
        self.cleanup_errors = list(cleanup_errors)
        cleanup_summary = "; ".join(str(error) for error in cleanup_errors)
        if primary_error is None:
            message = (
                f"{len(cleanup_errors)} cleanup operation(s) failed: "
                f"{cleanup_summary}"
            )
        else:
            message = (
                f"{primary_error} and {len(cleanup_errors)} cleanup "
                f"operation(s) failed: {cleanup_summary}"
            )
        super().__init__(message)


def _raise_lifecycle_errors(
    primary_error: BaseException | None,
    cleanup_errors: Sequence[BaseException],
) -> None:
    if primary_error is not None:
        if cleanup_errors:
            raise ForkBankLifecycleError(
                primary_error,
                cleanup_errors,
            ) from primary_error
        raise primary_error
    if len(cleanup_errors) == 1:
        raise cleanup_errors[0]
    if cleanup_errors:
        raise ForkBankLifecycleError(None, cleanup_errors)


class SimpleDictBank(AbstractForkGenerator):

    lock = Lock()
    warmed_environments: Dict[str, Dict[str, List[str]]] = {}

    def __init__(
        self,
        env_class: Type[ToolCallEnv],
        tvcache_base_url: str = "http://localhost:8001",
        env_kwargs: dict[str, Any] | None = None,
    ):
        self.env_class = env_class
        self.env_kwargs = dict(env_kwargs or {})
        self.cache_client = AsyncTVCacheClient(base_url=tvcache_base_url)
        self.environment_forks = 0
        logger.info(f"SimpleDictBank initialized with env_class: {env_class.__name__}")

    def _create_env(
        self,
        env_id: str | None = None,
        task_name: str = "default_task",
    ) -> ToolCallEnv:
        return self.env_class(
            env_id=env_id,
            task_name=task_name,
            **self.env_kwargs,
        )

    async def deposit(self, task_name, rollout_count):
        logger.info(f"Starting deposit for task_name='{task_name}', rollout_count={rollout_count}")
        forks: Dict[str, List[str]] = {}
        created_forks: List[ToolCallEnv] = []
        stored_env_ids: List[str] = []
        primary_error: BaseException | None = None

        try:
            stored_env_ids = await self.cache_client.get_all_envs(
                task_name=task_name
            )
            logger.debug(f"Retrieved {len(stored_env_ids)} stored environment IDs: {stored_env_ids}")

            for env_id in stored_env_ids:
                logger.debug(f"Creating forks for env_id='{env_id}'")
                env_obj = self._create_env(env_id=env_id, task_name=task_name)
                forks[env_id] = []

                for i in range(rollout_count):
                    fork_obj = await env_obj.fork()
                    created_forks.append(fork_obj)
                    self.environment_forks += 1
                    forks[env_id].append(fork_obj.get_id())
                    logger.debug(f"Created fork {i+1}/{rollout_count} for env_id='{env_id}': {fork_obj}")

                logger.info(f"Completed {rollout_count} forks for env_id='{env_id}'")

            # Prime the root environment.
            logger.debug("Creating root environment forks")
            forks[ROOT_KEY] = []

            for i in range(rollout_count):
                root_obj = self._create_env(task_name=task_name)
                root_primary_error: BaseException | None = None
                root_cleanup_errors: List[BaseException] = []
                fork_obj: ToolCallEnv | None = None
                try:
                    fork_obj = await root_obj.fork()
                    created_forks.append(fork_obj)
                    self.environment_forks += 1
                    forks[ROOT_KEY].append(fork_obj.get_id())
                except BaseException as error:
                    root_primary_error = error

                try:
                    await root_obj.stop()
                except BaseException as error:
                    root_cleanup_errors.append(error)

                _raise_lifecycle_errors(
                    root_primary_error,
                    root_cleanup_errors,
                )
                assert fork_obj is not None
                logger.debug(f"Created root fork {i+1}/{rollout_count}: {fork_obj.get_id()}")

            logger.info(f"Completed {rollout_count} root forks")
        except BaseException as error:
            primary_error = error

        cleanup_errors: List[BaseException] = []
        for env_id in stored_env_ids:
            logger.debug(
                "Unreferencing env_id='%s' for task '%s'",
                env_id,
                task_name,
            )
            try:
                await self.cache_client.unref(
                    env_id,
                    task_name=task_name,
                )
            except BaseException as error:
                cleanup_errors.append(error)

        if primary_error is not None or cleanup_errors:
            if primary_error is None:
                primary_error = cleanup_errors.pop(0)
            for fork_obj in reversed(created_forks):
                try:
                    await fork_obj.stop()
                except BaseException as error:
                    cleanup_errors.append(error)
            _raise_lifecycle_errors(primary_error, cleanup_errors)

        with self.lock:
            if task_name not in self.warmed_environments:
                self.warmed_environments[task_name] = {}
                logger.debug(f"Initialized warmed_environments for task_name='{task_name}'")
            
            task_environments = self.warmed_environments[task_name]

            for env_id in forks:
                if env_id not in task_environments:
                    task_environments[env_id] = []
                    logger.debug(f"Initialized fork list for env_id='{env_id}' in task '{task_name}'")
                
                before_count = len(task_environments[env_id])
                task_environments[env_id].extend(forks[env_id])
                after_count = len(task_environments[env_id])
                logger.info(f"Added {len(forks[env_id])} forks to env_id='{env_id}' (before: {before_count}, after: {after_count})")
            
            total_forks = sum(len(envs) for envs in task_environments.values())
            logger.info(f"Deposit complete for task '{task_name}': {len(task_environments)} parent envs, {total_forks} total forks")
            logger.debug(f"Warmed environments breakdown: {[(env_id, len(envs)) for env_id, envs in task_environments.items()]}")

        logger.info(f"Deposit completed successfully for task_name='{task_name}'")

    def get_stats(self) -> dict[str, int]:
        return {"environment_forks": self.environment_forks}

    async def close(self) -> None:
        await self.cache_client.close()


    async def withdraw(self, task_name):
        logger.info(f"Starting withdraw for task_name='{task_name}'")
        task_environments = {}

        with self.lock:
            if task_name not in self.warmed_environments:
                logger.warning(f"Task '{task_name}' not found in warmed_environments during withdraw")
                return
            
            task_environments = self.warmed_environments[task_name]
            parent_env_count = len(task_environments)
            total_fork_count = sum(len(envs) for envs in task_environments.values())
            logger.info(f"Withdrawing {parent_env_count} parent envs with {total_fork_count} total forks for task '{task_name}'")
            
            self.warmed_environments[task_name] = {}
            logger.debug(f"Cleared warmed_environments for task_name='{task_name}'")
        
        cleanup_errors: List[BaseException] = []
        failed_forks: Dict[str, List[str]] = {}
        for parent_env in task_environments:
            forked_envs = task_environments[parent_env]
            logger.debug(f"Stopping {len(forked_envs)} forked environments for parent_env='{parent_env}'")
            
            for idx, f_env_id in enumerate(forked_envs):
                logger.debug(f"Stopping fork {idx+1}/{len(forked_envs)}: {f_env_id}")
                f_env_obj = self._create_env(env_id=f_env_id, task_name=task_name)
                try:
                    await f_env_obj.stop()
                except BaseException as cleanup_error:
                    cleanup_errors.append(cleanup_error)
                    failed_forks.setdefault(parent_env, []).append(f_env_id)
            
            logger.info(f"Stopped all {len(forked_envs)} forks for parent_env='{parent_env}'")

        if failed_forks:
            with self.lock:
                current_environments = self.warmed_environments.setdefault(
                    task_name,
                    {},
                )
                for parent_env, fork_ids in failed_forks.items():
                    current_environments.setdefault(parent_env, []).extend(
                        fork_ids
                    )

        if len(cleanup_errors) == 1:
            raise cleanup_errors[0]
        if cleanup_errors:
            details = "; ".join(
                f"{type(error).__name__}: {error}"
                for error in cleanup_errors
            )
            raise RuntimeError(
                f"{len(cleanup_errors)} fork cleanup operation(s) failed: "
                f"{details}"
            ) from cleanup_errors[0]

        logger.info(f"Withdraw completed for task_name='{task_name}'")
    
    def get_forked_env(self, task_name, parent_env_id) -> str:
        logger.debug(f"get_forked_env called for task_name='{task_name}', parent_env_id='{parent_env_id}'")
        
        with self.lock:
            if task_name not in self.warmed_environments:
                logger.warning(f"Task '{task_name}' not found in warmed_environments")
                return None
            
            task_environments = self.warmed_environments[task_name]

            if len(task_environments) == 0:
                logger.warning(f"No warmed environments available for task '{task_name}'")
                return None
            
            if parent_env_id not in task_environments:
                logger.warning(f"Parent env_id '{parent_env_id}' not found in task '{task_name}'. Available: {list(task_environments.keys())}")
                return None
            
            if len(task_environments[parent_env_id]) == 0:
                logger.warning(f"No forks available for parent_env_id '{parent_env_id}' in task '{task_name}'")
                return None
            
            forked_env = task_environments[parent_env_id].pop()
            remaining = len(task_environments[parent_env_id])
            logger.info(f"Retrieved fork '{forked_env}' from parent '{parent_env_id}' (remaining: {remaining})")
            
            return forked_env
        
        return None
