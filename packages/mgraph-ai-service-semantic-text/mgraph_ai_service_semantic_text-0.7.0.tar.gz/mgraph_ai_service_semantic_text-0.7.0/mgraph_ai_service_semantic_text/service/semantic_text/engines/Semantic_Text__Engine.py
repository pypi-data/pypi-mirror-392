from typing                                                                                 import Dict
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                import Safe_Str__Text
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria     import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode  import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification    import Safe_Float__Text__Classification


class Semantic_Text__Engine(Type_Safe):                                        # Base class for all text classification engines
    engine_mode : Enum__Text__Classification__Engine_Mode                      # Engine mode identifier

    def classify_text(self                 ,                                   # Classify text and return all 4 sentiment scores
                      text : Safe_Str__Text
                 ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:  # Returns all 4 scores (positive/negative/neutral/mixed)
        raise NotImplementedError("Subclass must implement classify_text() method")
