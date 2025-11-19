from typing                                                                                 import Dict
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text               import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash          import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria     import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode  import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification    import Safe_Float__Text__Classification


class Schema__Semantic_Text__Classification(Type_Safe):
    text                : Safe_Str__Comprehend__Text
    text__hash          : Safe_Str__Hash                            = None
    text__classification: Dict[Enum__Text__Classification__Criteria,
                               Safe_Float__Text__Classification    ]
    engine_mode         : Enum__Text__Classification__Engine_Mode

