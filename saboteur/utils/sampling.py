import random


def uniform_sample_from_dict(
    data: dict, stop_threshold: float = 0.5, rng: random.Random | None = None
) -> tuple[list[str], object]:
    key_paths: list[str] = []
    random_source = rng or random

    def _sample(d: dict) -> object:
        probability = random_source.uniform(0, 1)
        key_list = list(d.keys())
        random_key = random_source.choice(key_list)
        key_paths.append(random_key)
        random_value = d[random_key]
        if probability < stop_threshold or not isinstance(random_value, dict):
            return random_value
        return _sample(d[random_key])

    random_value = _sample(data)
    return key_paths, random_value


def sample_unique_paths_from_dict(
    data: dict,
    count: int = 1,
    stop_threshold: float = 0.5,
    rng: random.Random | None = None,
) -> list[tuple[list[str], object]]:
    if count <= 0:
        return []

    random_source = rng or random
    samples: list[tuple[list[str], object]] = []
    seen_paths: set[tuple[str, ...]] = set()
    max_attempts = max(count * 10, 10)

    for _ in range(max_attempts):
        key_paths, value = uniform_sample_from_dict(
            data=data,
            stop_threshold=stop_threshold,
            rng=random_source,
        )
        path_key = tuple(key_paths)
        if path_key in seen_paths:
            continue

        seen_paths.add(path_key)
        samples.append((key_paths, value))
        if len(samples) >= count:
            break

    return samples
