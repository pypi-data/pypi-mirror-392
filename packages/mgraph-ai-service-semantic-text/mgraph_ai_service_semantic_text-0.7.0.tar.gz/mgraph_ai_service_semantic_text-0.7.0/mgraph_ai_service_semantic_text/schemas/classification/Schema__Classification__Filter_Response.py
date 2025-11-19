from typing                                                                                         import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                       import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                  import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria             import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification            import Safe_Float__Text__Classification
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode import Enum__Classification__Output_Mode


class Schema__Classification__Filter_Response(Type_Safe):                                               # Response with filtered hashes based on criteria
    filtered_hashes         : List[Safe_Str__Hash]                                                      # List of hash IDs that matched filter
    filtered_with_text      : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]                          # Hash → text mapping (if output_mode includes text)
    filtered_with_ratings   : Dict[Safe_Str__Hash, Dict[Enum__Text__Classification__Criteria,
                                                        Safe_Float__Text__Classification]]              # Hash → {all 4 criteria → scores}
    classification_criteria : Enum__Text__Classification__Criteria                                      # Criteria used for filtering
    output_mode             : Enum__Classification__Output_Mode                                         # Output format used
    total_hashes            : Safe_UInt                                                                 # Total number of hashes in input
    filtered_count          : Safe_UInt                                                                 # Number of hashes that passed filter
    success                 : bool                                                                      # Whether filtering succeeded
