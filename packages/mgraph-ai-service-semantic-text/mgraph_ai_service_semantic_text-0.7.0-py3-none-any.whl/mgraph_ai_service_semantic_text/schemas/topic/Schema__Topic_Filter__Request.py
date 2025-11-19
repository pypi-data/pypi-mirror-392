from typing                                                                                             import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                           import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                      import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Logic_Operator  import Enum__Classification__Logic_Operator
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode     import Enum__Classification__Output_Mode
from mgraph_ai_service_semantic_text.schemas.topic.enums.Enum__Classification__Topic                    import Enum__Classification__Topic
from mgraph_ai_service_semantic_text.schemas.topic.safe_float.Safe_Float__Topic_Confidence              import Safe_Float__Topic_Confidence


class Schema__Topic_Filter__Request(Type_Safe):                                # Request to filter hashes by topic criteria
    hash_mapping            : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text] # Hash → original text mapping
    required_topics         : List[Enum__Classification__Topic]                # List of topics that must match
    min_confidence          : Safe_Float__Topic_Confidence                     # Minimum confidence threshold (0.0-1.0)
    logic_operator          : Enum__Classification__Logic_Operator
    output_mode             : Enum__Classification__Output_Mode
