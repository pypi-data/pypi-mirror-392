from typing                                                                                         import Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                               import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                      import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from osbot_utils.utils.Misc                                                                         import random_number
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria             import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode          import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification            import Safe_Float__Text__Classification
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine            import Semantic_Text__Engine


class Semantic_Text__Engine__Random(Semantic_Text__Engine):                                                 # Pure random classification engine
    engine_mode : Enum__Text__Classification__Engine_Mode = Enum__Text__Classification__Engine_Mode.RANDOM  # Random mode

    @type_safe
    def classify_text(self                 ,                                                                # Generate random sentiment scores
                      text : Safe_Str__Text
                 ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:         # All 4 normalized scores (sum to 1.0)

        scores = self.generate_scores()                                                                     # Generate 4 random scores that sum to 1.0

        return scores

    def generate_scores(self                                                                                # Generate 4 random scores
                   ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:       # 4 scores summing to 1.0

        raw_scores = [random_number(0, 100) / 100 for _ in range(4)]
        total = sum(raw_scores)

        criteria_list = [Enum__Text__Classification__Criteria.POSITIVE ,        # Map samples to criteria in consistent order
                         Enum__Text__Classification__Criteria.NEGATIVE ,
                         Enum__Text__Classification__Criteria.NEUTRAL  ,
                         Enum__Text__Classification__Criteria.MIXED    ]

        scores = Type_Safe__Dict(expected_key_type   = Enum__Text__Classification__Criteria,
                                 expected_value_type = Safe_Float__Text__Classification)
        for i, criterion in enumerate(criteria_list):
            normalized_value = raw_scores[i] / total
            scores[criterion] = Safe_Float__Text__Classification(normalized_value)
        return scores
