from typing                                                                                             import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                           import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                    import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                      import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Logic_Operator  import Enum__Classification__Logic_Operator
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode     import Enum__Classification__Output_Mode
from mgraph_ai_service_semantic_text.schemas.topic.enums.Enum__Classification__Topic                    import Enum__Classification__Topic
from mgraph_ai_service_semantic_text.schemas.topic.safe_float.Safe_Float__Topic_Confidence              import Safe_Float__Topic_Confidence


class Schema__Topic_Filter__Response(Type_Safe):                                                # Response with filtered hashes based on topic criteria
    filtered_hashes         : List[Safe_Str__Hash]                                              # List of hash IDs that matched filters
    filtered_with_text      : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]                  # Hash → text mapping (if output_mode includes text)
    filtered_with_scores    : Dict[Safe_Str__Hash, Dict[Enum__Classification__Topic,
                                                        Safe_Float__Topic_Confidence ]]         # Hash → {topic → confidence} (if output_mode includes scores)
    topics_used             : List[Enum__Classification__Topic]                                 # List of Enum__Classification__Topic used in filtering
    logic_operator          : Enum__Classification__Logic_Operator                              # Enum__Classification__Logic_Operator used - typed as None
    output_mode             : Enum__Classification__Output_Mode                                 # Enum__Classification__Output_Mode used - typed as None
    total_hashes            : Safe_UInt                                                         # Total number of hashes in input
    filtered_count          : Safe_UInt                                                         # Number of hashes that passed filters
    success                 : bool                                                              # Whether filtering succeeded
