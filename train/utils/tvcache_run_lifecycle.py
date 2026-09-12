from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any, Type
from uuid import uuid4

import httpx

from tvclient.tools.tool_call_env import ToolCallEnv
from tvclient.utils.async_tvcache_client import AsyncTVCacheClient


TRANSPORT_RETRY_DELAY_SECONDS = 1.0


class TVCacheRunLifecycleError(RuntimeError):
    def __init__(
        self,
        primary_error: BaseException | None,
        cleanup_errors: Sequence[BaseException],
    ) -> None:
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
            raise TVCacheRunLifecycleError(
                primary_error,
                cleanup_errors,
            ) from primary_error
        raise primary_error

    if len(cleanup_errors) == 1:
        raise cleanup_errors[0]
    if cleanup_errors:
        raise TVCacheRunLifecycleError(None, cleanup_errors)


def _is_transport_failure(error: BaseException) -> bool:
    if isinstance(error, httpx.TransportError):
        return True
    if not isinstance(error, TVCacheRunLifecycleError):
        return False
    return (
        error.primary_error is None
        and bool(error.cleanup_errors)
        and all(
            _is_transport_failure(cleanup_error)
            for cleanup_error in error.cleanup_errors
        )
    )


class TVCacheRunLifecycle:
    """Own cache-resident environments until final run teardown."""

    def __init__(
        self,
        environment_class: Type[ToolCallEnv],
        tvcache_base_url: str,
        env_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.environment_class = environment_class
        self.env_kwargs = dict(env_kwargs or {})
        self.client = AsyncTVCacheClient(base_url=tvcache_base_url)
        self._pending_task_drains: dict[str, str] = {}
        self._pending_environment_stops: dict[
            tuple[str, str],
            str,
        ] = {}
        self._pending_drain_acks: dict[str, str] = {}

    async def __aenter__(self) -> "TVCacheRunLifecycle":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> bool:
        try:
            await self._close_after_transport_failures()
        except BaseException as cleanup_error:
            if exc_value is None:
                raise

            if (
                isinstance(cleanup_error, TVCacheRunLifecycleError)
                and cleanup_error.primary_error is None
            ):
                cleanup_errors = cleanup_error.cleanup_errors
            else:
                cleanup_errors = [cleanup_error]
            raise TVCacheRunLifecycleError(
                exc_value,
                cleanup_errors,
            ) from exc_value

        return False

    async def _close_after_transport_failures(self) -> None:
        while True:
            try:
                await self.close()
            except BaseException as error:
                if not _is_transport_failure(error):
                    raise
                await asyncio.sleep(TRANSPORT_RETRY_DELAY_SECONDS)
            else:
                return

    def register_task(self, task_name: str) -> None:
        if not isinstance(task_name, str) or not task_name:
            raise ValueError("task_name must be a non-empty string")
        if (
            task_name not in self._pending_task_drains
            and task_name not in self._pending_drain_acks
        ):
            self._pending_task_drains[task_name] = uuid4().hex

    async def close(self) -> None:
        cleanup_errors: list[BaseException] = []

        for task_name, drain_id in sorted(
            self._pending_task_drains.items()
        ):
            try:
                env_ids = await self.client.drain_task(
                    task_name,
                    drain_id,
                )
            except BaseException as error:
                cleanup_errors.append(error)
                continue

            del self._pending_task_drains[task_name]
            self._pending_drain_acks[task_name] = drain_id
            for env_id in env_ids:
                self._pending_environment_stops[(task_name, env_id)] = (
                    f"{drain_id}:{env_id}"
                )

        for (task_name, env_id), operation_id in sorted(
            self._pending_environment_stops.items()
        ):
            try:
                environment = self.environment_class(
                    env_id=env_id,
                    task_name=task_name,
                    **self.env_kwargs,
                )
                await environment.stop(operation_id=operation_id)
            except BaseException as error:
                cleanup_errors.append(error)
            else:
                del self._pending_environment_stops[(task_name, env_id)]

        tasks_with_pending_stops = {
            task_name
            for task_name, _ in self._pending_environment_stops
        }
        for task_name, drain_id in sorted(
            self._pending_drain_acks.items()
        ):
            if task_name in tasks_with_pending_stops:
                continue

            try:
                await self.client.ack_task_drain(
                    task_name,
                    drain_id,
                )
            except BaseException as error:
                cleanup_errors.append(error)
            else:
                del self._pending_drain_acks[task_name]

        try:
            await self.client.close()
        except BaseException as error:
            cleanup_errors.append(error)

        _raise_lifecycle_errors(None, cleanup_errors)
