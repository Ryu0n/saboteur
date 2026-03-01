import copy
import time
import random
from typing import Dict, Any, List
from saboteur.domain.base.runner import BaseRunner
from saboteur.domain.mutation.configs import MutationConfig
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.domain.mutation.results import MutationResult
from saboteur.utils.sampling import uniform_sample_from_dict


class MutationRunner(
    BaseRunner[
        MutationConfig,
        MutationStrategy,
        MutationContext,
        MutationResult,
    ]
):
    def _mutate(self, context: MutationContext) -> List[object]:
        mutated = []
        for strategy in self._get_applicable_strategies(context):
            mutated_value = strategy.apply(context)
            mutated.append(mutated_value)
        return mutated

    def _wrap_into_contexts(self, data: Dict[str, Any]) -> List[MutationContext]:
        key_paths, value = uniform_sample_from_dict(data)
        return [
            MutationContext(
                key_paths=key_paths, original_value=value, original_type=type(value)
            )
        ]

    def mutate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        _data = copy.deepcopy(params)
        contexts = self._wrap_into_contexts(_data)

        for context in contexts:
            candidates = self._get_applicable_strategies(context)
            if not candidates:
                continue
            if self._config.apply_all_strategies:
                for strategy in candidates:
                    mutated = strategy.apply(context)
                    _data = mutated.mutate(_data)
            else:
                strategies_to_apply = random.sample(
                    population=candidates,
                    k=self._config.num_strategies_to_apply,
                )
                for strategy in strategies_to_apply:
                    mutated = strategy.apply(context)
                    _data = mutated.mutate(_data)

        return _data

    def run(self) -> MutationResult:
        start = time.monotonic()
        mutated = self.mutate(self._config.original_data)
        elasped = time.monotonic() - start
        return MutationResult(
            result=mutated,
            elapsed_time=elasped,
        )
