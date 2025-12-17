import copy
import random

from typing import List, Dict, Any
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.domain.mutation.configs import MutationConfig


class Saboteur:
    def __init__(self, config: MutationConfig):
        self.__config = config
    
    def _get_applicable_strategies(self, context: MutationContext) -> List[MutationStrategy]:
        return [s for s in self.__config.strategies if s.is_applicable(context)]
    
    def _mutate(self, context: MutationContext) -> List[object]:
        mutated = []
        for strategy in self._get_applicable_strategies(context):
            mutated_value = strategy.apply(context)
            mutated.append(mutated_value)
        return mutated
    
    def _wrap_into_mutations(self, data: Dict[str, Any]) -> List[MutationContext]:
        if self.__config.apply_all_keys:
            return [
                MutationContext(
                    path=key,
                    original_value=value,
                    original_type=type(value)
                )
                for key, value in data.items()
            ]
        else:
            key = random.choice(list(data.keys()))
            value = data[key]
            return [
                MutationContext(
                    path=key,
                    original_value=value,
                    original_type=type(value)
                )
            ] 
    
    def attack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        _data = copy.deepcopy(data)
        contexts = self._wrap_into_mutations(_data)
        
        for context in contexts:
            candidates = self._get_applicable_strategies(context)
            if not candidates:
                continue
            if self.__config.apply_all_strategies:
                for strategy in candidates:
                    mutated_value = strategy.apply(context)
                    _data[context.path] = mutated_value
            else:
                strategy = random.choice(candidates)
                mutated_value = strategy.apply(context)
                _data[context.path] = mutated_value
        
        return _data