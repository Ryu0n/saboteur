from saboteur.domain.base.runners import BaseRunner, AsyncBaseRunner


class Saboteur:
    """Facade for the saboteur mutation framework."""

    def __init__(
        self, runners: list[BaseRunner] = [], async_runners: list[AsyncBaseRunner] = []
    ):
        self.__runners = {
            id(runner): runner for runner in runners if isinstance(runner, BaseRunner)
        }
        self.__async_runners = {
            id(runner): runner
            for runner in async_runners
            if isinstance(runner, AsyncBaseRunner)
        }

    def register_runner(self, runner: BaseRunner):
        """Register a new runner to the saboteur."""
        self.__runners[id(runner)] = runner

    def unregister_runner(self, runner: BaseRunner):
        """Unregister a runner from the saboteur."""
        if id(runner) in self.__runners:
            del self.__runners[id(runner)]

    def list_runners(self) -> list[BaseRunner]:
        """List all registered runners."""
        return list(self.__runners.values())

    def get_runner(self, runner_id: int) -> BaseRunner:
        """Get a runner by its ID."""
        return self.__runners.get(runner_id)

    def run(self) -> list:
        """Run all registered runners and return their results."""
        results = {}
        for id_runner, runner in self.__runners.items():
            result = runner.run()
            results[id_runner] = result
        return results

    async def run_async(self) -> list:
        results = {}
        for id_runner, runner in self.__async_runners.items():
            result = await runner.run()
            results[id_runner] = result
        return results
