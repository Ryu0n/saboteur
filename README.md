# Saboteur

[![PyPI version](https://badge.fury.io/py/saboteur.svg)](https://badge.fury.io/py/saboteur)

A simple and extensible data mutation library for Chaos Engineering in Python.

## 🤔 What is Saboteur?

**Saboteur** is a lightweight Python library designed to test the robustness of your data processing logic. It helps you practice Chaos Engineering by intentionally and randomly injecting faulty or unexpected data into your system.

By "attacking" your data with various mutation strategies, Saboteur helps you uncover hidden bugs, handle edge cases gracefully, and build more resilient applications.

## ✨ Key Features

-   **Simple API**: Get started in seconds with the intuitive `.run()` or `.run_async()` methods.
-   **Randomized Mutations**: Automatically selects a random field and applies a random, applicable mutation to simulate real-world unpredictability.
-   **API Load Testing**: Simulate heavy traffic and test the performance of your endpoints using customizable load strategies.
-   **Extensible**: Easily create and add your own custom mutation or load strategies.
-   **Lightweighted Dependencies**: A pure Python library that can be dropped into any project without extra baggage.

## 💾 Installation

Install Saboteur directly from PyPI:

```bash
# pip
pip install saboteur

# poetry
pip install poetry && poetry add saboteur
```

## 🚀 Quick Start

Using Saboteur is straightforward. Import the `Saboteur` class and the desired strategies, then call the `mutate` method on your data.

```python
from saboteur.application.facade import Saboteur
from saboteur.infrastructure.mutation.strategies.injections import NullInjectionStrategy
from saboteur.infrastructure.mutation.strategies.flippings import TypeFlipStrategy
from saboteur.domain.mutation.configs import MutationConfig
from saboteur.domain.mutation.runners import MutationRunner

# 0. Prepare your data
mock_data = {
    "user_id": 12345,
    "username": "test_user",
    "is_active": True,
    "score": 987
}

# 1. Define the strategies you want to use
strategies = [
    NullInjectionStrategy(),
    TypeFlipStrategy(),
]

# 2. Set configuration what you want
config = MutationConfig(
    strategies=strategies,
    apply_all_strategies=True,
    original_data=mock_data,
    max_targets=2,
    seed=42,
)

# 3. Initialize runners with corresponding configuration within Sabeteur Facade.
saboteur = Saboteur(
    runners=[
        MutationRunner(
            config=config,
        )
    ]
)

# 4. Mutate the data! (Run all runners respectively)
# Saboteur will randomly pick one key (e.g., "user_id") and apply one
# applicable strategy (e.g., TypeFlipStrategy).
results = saboteur.run()

# 5. Each runner's results is returned! (Key is id of runner object)
# Example output:
# {
#   4332166016: MutationResult(
#     result={'age': None, 'name': None, 'active': True, 'score': None, 'nested': {...}},
#     created_at='2026-03-02T07:47:15.115957+09:00',
#     elapsed_time=3.724999260157347e-05,
#     applied_mutations=[
#       MutationTrace(key_path=['age'], strategy='NullInjectionStrategy', original_value=25, mutated_value=None),
#       MutationTrace(key_path=['name'], strategy='NullInjectionStrategy', original_value='test_user', mutated_value=None),
#     ]
#   )
# }
print(results)
```

`MutationConfig.max_targets` lets you mutate more than one randomly selected field in a single run, and `MutationConfig.seed` makes the selection reproducible.

### ⚡ Load Testing Quick Start

Saboteur now supports API load testing. You can run linear or custom load strategies asynchronously.

```python
import asyncio
from saboteur.application.facade import Saboteur
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.runners import LoadRunner
from saboteur.infrastructure.load.strategies.linear import LinearLoadStrategy


async def main():
    # 1. Define load strategies
    strategies = [LinearLoadStrategy()]

    # 2. Configure the load test
    config = LoadConfig(
        strategies=strategies,
        url="https://api.example.com/data",
        method="GET",
        duration_seconds=10,
        interval_seconds=1.0,
        concurrency=5,
    )

    # 3. Initialize runner
    runner = LoadRunner(config=config)
    saboteur = Saboteur(async_runners=[runner])

    # 4. Run the load test!
    results = await saboteur.run_async()
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

Each `LoadResult` now includes raw request records in `result` and per-strategy summaries in `strategy_reports`, including `total_requests`, `success_rate`, latency metrics, and status code counts.

## 🛠️ Available Strategies

Saboteur comes with a set of built-in strategies to get you started.

## Strategies for `MutationRunner`

#### `NullInjectionStrategy`

Replaces the original value of a field with `None`. This is useful for testing how your code handles missing or null data.

-   **Applicable when**: The field value is not `None`.
-   **Mutation**: `value` -> `None`

#### `TypeFlipStrategy(to_type=None)`

Changes the data type of a field. By default a target type is randomly chosen at instantiation time from `(int, float, str, bool, list)`. You can pin a specific type by passing `to_type` explicitly.

-   **Applicable when**: The current value can be successfully cast to the target type without raising `ValueError` or `TypeError`.
-   **Mutation**: `value` -> `to_type(value)` (e.g., `123` -> `'123'`, `'3.14'` -> `3.14`)

> **Note**: Each `TypeFlipStrategy()` call independently draws a random target type. Two instances created without arguments are not guaranteed to use the same type.

#### `RandomizationStrategy`

Replaces a value with a randomized value of the same type. This is useful for testing how your system handles a wide range of valid but unexpected inputs. Saboteur provides several randomization strategies based on data type.

-   **`IntegerRandomizationStrategy(from_value: int = -1000, to_value: int = 1000)`**
    -   **Applicable when**: The field value is an `int`.
    -   **Mutation**: Replaces the value with a random integer within the specified range (`from_value` to `to_value`).

-   **`FloatRandomizationStrategy(from_value: float = -1000.0, to_value: float = 1000.0)`**
    -   **Applicable when**: The field value is a `float`.
    -   **Mutation**: Replaces the value with a random float within the specified range.

-   **`StringRandomizationStrategy(length: int = 10)`**
    -   **Applicable when**: The field value is a `str`.
    -   **Mutation**: Replaces the value with a random alphanumeric string of the specified `length`.

-   **`BooleanRandomizationStrategy`**
    -   **Applicable when**: The field value is a `bool`.
    -   **Mutation**: Replaces the value with a randomly chosen `True` or `False`.

-   **`ListRandomizationStrategy`**
    -   **Applicable when**: The field value is a non-empty `list`.
    -   **Mutation**: Creates a new list of the same length by randomly sampling elements from the original list (with replacement).

-   **`DictRandomizationStrategy`**
    -   **Applicable when**: The field value is a `dict` with more than one key.
    -   **Mutation**: Reassigns values to keys in a random order, so the key→value mapping changes (e.g., `{"a": 1, "b": 2}` → `{"a": 2, "b": 1}`).

## Strategies for `LoadRunner`

#### `LinearLoadStrategy`

Sends requests at a fixed interval for a specified duration.

-   **Description**: Distributes `concurrency` number of requests every `interval_seconds`.
-   **Configurable via**: `LoadConfig` (duration, interval, concurrency).

#### `ExponentialBackoffLoadStrategy(initial_interval, multiplier, max_interval, jitter)`

Sends request batches with exponentially increasing wait times between each batch.

-   **Description**: After each batch, the wait time grows by `multiplier` up to `max_interval`. When `jitter=True` (default), a random value between `0` and the computed wait time is used instead to avoid thundering-herd effects.
-   **Configurable via**: `LoadConfig` plus constructor parameters.

```python
from saboteur.infrastructure.load.strategies.backoff import ExponentialBackoffLoadStrategy

strategy = ExponentialBackoffLoadStrategy(
    initial_interval=1.0,   # start with 1 s
    multiplier=2.0,         # double each time
    max_interval=60.0,      # cap at 60 s
    jitter=True,            # add randomness (default)
)
```

## 🔧 Managing Runners at Runtime

`Saboteur` exposes management methods so you can register and unregister runners after construction.

```python
saboteur = Saboteur()

# Sync runners
saboteur.register_runner(runner)
saboteur.unregister_runner(runner)
saboteur.list_runners()          # -> list[BaseRunner]
saboteur.get_runner(id(runner))  # -> BaseRunner | None

# Async runners
saboteur.register_async_runner(async_runner)
saboteur.unregister_async_runner(async_runner)
saboteur.list_async_runners()          # -> list[AsyncBaseRunner]
saboteur.get_async_runner(id(runner))  # -> AsyncBaseRunner | None
```

## ✍️ Creating a Custom Strategy

You can easily create your own strategies by inheriting from `MutationStrategy` and implementing two methods: `is_applicable` and `apply`.

`MutationContext` exposes the following fields:

| Field | Description |
|---|---|
| `key_paths` | List of keys representing the nested path to the target field. |
| `value` | The current value at that path (before or after a mutation). |
| `value_type` | The Python type of `value`. |

Here's an example of a `BooleanFlipStrategy` that flips `True` to `False` and vice-versa.

```python
# custom_strategies.py
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.domain.mutation.configs import MutationConfig


class BooleanFlipStrategy(MutationStrategy):
    """Flips a boolean value."""

    def is_applicable(self, context: MutationContext) -> bool:
        # This strategy only applies to boolean types
        return context.value_type is bool

    def apply(self, context: MutationContext) -> MutationContext:
        # Return a new MutationContext with the flipped value
        return MutationContext(
            key_paths=context.key_paths,
            value=not context.value,
            value_type=bool,
        )


# You can then use it with Saboteur:
strategies = [
    BooleanFlipStrategy(),
    # ... other strategies
]

config = MutationConfig(
    strategies=strategies,
    original_data={"is_active": True},
)
```

## 🤝 Contributing

Contributions are welcome! Whether it's adding new strategies, improving documentation, or fixing bugs, please feel free to open an issue or submit a pull request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 🗺️ Roadmap

Saboteur is expanding to become a comprehensive resiliency testing tool. Future versions will include:
-   **More Load Strategies**: Poisson distribution, ramping (step-up) load, etc.
-   **Enhanced Reporting**: Visual summaries and performance metrics for load tests.
-   **Protocol Support**: Expanding beyond HTTP (e.g., gRPC, WebSocket).

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
