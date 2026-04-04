import copy
import time
import random
from typing import Dict, Any, List

from saboteur.domain.base.runners import BaseRunner
from saboteur.domain.mutation.configs import MutationConfig
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.domain.mutation.results import MutationResult, MutationTrace
from saboteur.utils.sampling import sample_unique_paths_from_dict


class MutationRunner(
    BaseRunner[
        MutationConfig,
        MutationStrategy,
        MutationContext,
        MutationResult,
    ]
):
    def _wrap_into_contexts(self, data: Dict[str, Any]) -> List[MutationContext]:
        sampled_paths = sample_unique_paths_from_dict(
            data=data,
            count=self._config.max_targets,
            stop_threshold=self._config.stop_threshold,
        )
        return [
            MutationContext(
                key_paths=key_paths, original_value=value, original_type=type(value)
            )
            for key_paths, value in sampled_paths
        ]

    def mutate(self, params: Dict[str, Any]) -> tuple[Dict[str, Any], List[MutationTrace]]:
        _data = copy.deepcopy(params)
        contexts = self._wrap_into_contexts(_data)
        traces: List[MutationTrace] = []

        for context in contexts:
            candidates = self._get_applicable_strategies(context)
            if not candidates:
                continue
            if self._config.apply_all_strategies:
                strategies_to_apply = candidates
            else:
                strategies_to_apply = random.sample(
                    population=candidates,
                    k=min(len(candidates), self._config.num_strategies_to_apply),
                )

            for strategy in strategies_to_apply:
                mutated = strategy.apply(context)
                _data = mutated.mutate(_data)
                traces.append(
                    MutationTrace(
                        key_path=context.key_paths,
                        strategy=type(strategy).__name__,
                        original_value=context.original_value,
                        mutated_value=mutated.original_value,
                    )
                )

        return _data, traces

    def run(self) -> MutationResult:
        start = time.monotonic()
        random_state = random.getstate()
        if self._config.seed is not None:
            random.seed(self._config.seed)

        try:
            mutated, traces = self.mutate(self._config.original_data)
        finally:
            if self._config.seed is not None:
                random.setstate(random_state)

        elasped = time.monotonic() - start
        return MutationResult(
            result=mutated,
            applied_mutations=traces,
            elapsed_time=elasped,
        )
