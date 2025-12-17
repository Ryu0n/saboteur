import copy
import random

from typing import List, Dict, Any
from saboteur.domain.strategies import MutationStrategy
from saboteur.domain.contexts import MutationContext


class Saboteur:
    def __init__(self, strategies: List[MutationStrategy] = []):
        self.strategies = strategies
    
    def _get_applicable_strategies(self, context: MutationContext) -> List[MutationStrategy]:
        return [s for s in self.strategies if s.is_applicable(context)]
    
    def _mutate(self, context: MutationContext) -> List[object]:
        mutated = []
        for strategy in self._get_applicable_strategies(context):
            mutated_value = strategy.apply(context)
            mutated.append(mutated_value)
        return mutated
    
    def attack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = copy.deepcopy(data)
        keys = list(data.keys())
        
        target_key = random.choice(keys)
        original_value = data[target_key]
        
        context = MutationContext(
            path=target_key,
            original_value=original_value,
            original_type=type(original_value)
        )
        
        candidates = self._get_applicable_strategies(context)
        
        if not candidates:
            return result
        
        selected_strategy = random.choice(candidates)
        mutated_value = selected_strategy.apply(context)
        
        result[target_key] = mutated_value
        return result