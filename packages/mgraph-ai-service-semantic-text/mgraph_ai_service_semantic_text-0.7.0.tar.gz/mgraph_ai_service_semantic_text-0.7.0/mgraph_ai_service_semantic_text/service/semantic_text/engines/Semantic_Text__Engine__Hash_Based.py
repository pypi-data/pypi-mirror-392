from hashlib                                                                                        import md5
from typing                                                                                         import Dict
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                               import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                      import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                        import Safe_Str__Text
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria             import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode          import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification            import Safe_Float__Text__Classification
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine            import Semantic_Text__Engine


class Semantic_Text__Engine__Hash_Based(Semantic_Text__Engine):                # Deterministic hash-based classification engine
    engine_mode : Enum__Text__Classification__Engine_Mode = Enum__Text__Classification__Engine_Mode.TEXT_HASH  # Hash-based mode

    @type_safe
    def classify_text(self                 ,                                   # Generate all 4 sentiment scores using deterministic hashing
                      text : Safe_Str__Text
                 ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:  # All 4 normalized scores

        raw_scores = Type_Safe__Dict(expected_key_type   = Enum__Text__Classification__Criteria,
                                     expected_value_type = Safe_Float__Text__Classification    )

        for criterion in Enum__Text__Classification__Criteria:                                       # Generate raw hash-based score for each criterion
            raw_scores[criterion] = self.hash_score_for_criterion(text, criterion)

        normalized_scores = self._normalize_scores(raw_scores)                 # Normalize scores to sum to ~1.0

        return normalized_scores

    @type_safe
    def hash_score_for_criterion(self                ,                              # Generate deterministic hash-based score for specific criterion
                                   text      : Safe_Str__Text                      ,
                                   criterion : Enum__Text__Classification__Criteria
                              ) -> Safe_Float__Text__Classification:                 # Raw score (unnormalized)

        combined  = f"{text}_{criterion.value}"                                # Combine text + criterion for unique rating per criterion
        full_hash = md5(combined.encode()).hexdigest()                         # Get MD5 hash (32 hex characters)
        hash_int  = int(full_hash[:16], 16)                                    # Convert first 16 hex chars (64 bits) to integer
        rating    = (hash_int % 10000) / 10000.0                               # Normalize to 0.0-1.0 range using modulo for even distribution

        return rating

    @type_safe
    def _normalize_scores(self                              ,                  # Normalize raw scores to sum to 1.0 (probability distribution)
                          raw_scores : Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]
                     ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:  # Normalized scores

        total = sum(raw_scores.values())                                       # Calculate total for normalization

        if total == 0:                                                          # Handle edge case: all zeros (shouldn't happen with hash)
            equal_value = 1.0 / len(raw_scores)
            return {criterion: Safe_Float__Text__Classification(equal_value)
                    for criterion in Enum__Text__Classification__Criteria}

        normalized = Type_Safe__Dict(expected_key_type   = Enum__Text__Classification__Criteria,
                                     expected_value_type = Safe_Float__Text__Classification    )
        for criterion, score in raw_scores.items():                            # Normalize each score
            normalized_value = score / total
            normalized[criterion] = Safe_Float__Text__Classification(normalized_value)

        return normalized
