from saboteur.domain.base.runners import BaseRunner, AsyncBaseRunner


class Saboteur:
    """Facade for the saboteur mutation framework."""

    def __init__(
        self,
        runners: list[BaseRunner] | None = None,
        async_runners: list[AsyncBaseRunner] | None = None,
    ):
        self.__runners = {
            id(runner): runner
            for runner in (runners or [])
            if isinstance(runner, BaseRunner)
        }
        self.__async_runners = {
            id(runner): runner
            for runner in (async_runners or [])
            if isinstance(runner, AsyncBaseRunner)
        }

    # --- Sync runner management ---

    def register_runner(self, runner: BaseRunner):
        """Register a new sync runner."""
        self.__runners[id(runner)] = runner

    def unregister_runner(self, runner: BaseRunner):
        """Unregister a sync runner."""
        self.__runners.pop(id(runner), None)

    def list_runners(self) -> list[BaseRunner]:
        """List all registered sync runners."""
        return list(self.__runners.values())

    def get_runner(self, runner_id: int) -> BaseRunner | None:
        """Get a sync runner by its id()."""
        return self.__runners.get(runner_id)

    # --- Async runner management ---

    def register_async_runner(self, runner: AsyncBaseRunner):
        """Register a new async runner."""
        self.__async_runners[id(runner)] = runner

    def unregister_async_runner(self, runner: AsyncBaseRunner):
        """Unregister an async runner."""
        self.__async_runners.pop(id(runner), None)

    def list_async_runners(self) -> list[AsyncBaseRunner]:
        """List all registered async runners."""
        return list(self.__async_runners.values())

    def get_async_runner(self, runner_id: int) -> AsyncBaseRunner | None:
        """Get an async runner by its id()."""
        return self.__async_runners.get(runner_id)

    # --- Execution ---

    def run(self) -> dict:
        """Run all registered sync runners and return their results keyed by runner id."""
        results = {}
        for runner_id, runner in self.__runners.items():
            results[runner_id] = runner.run()
        return results

    async def run_async(self) -> dict:
        """Run all registered async runners and return their results keyed by runner id."""
        results = {}
        for runner_id, runner in self.__async_runners.items():
            results[runner_id] = await runner.run()
        return results
