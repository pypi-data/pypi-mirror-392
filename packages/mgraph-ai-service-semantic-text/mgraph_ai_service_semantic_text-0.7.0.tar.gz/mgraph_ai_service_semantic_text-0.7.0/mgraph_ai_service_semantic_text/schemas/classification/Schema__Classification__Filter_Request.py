from typing                                                                                         import Dict, Optional
from osbot_utils.type_safe.Type_Safe                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                               import Safe_Float
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                       import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                  import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria             import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode import Enum__Classification__Output_Mode
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Filter_Mode import Enum__Classification__Filter_Mode


class Schema__Classification__Filter_Request(Type_Safe):                       # Request to filter hashes by classification criteria
    hash_mapping            : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text] # Hash → original text mapping
    classification_criteria : Enum__Text__Classification__Criteria             # Specific criterion to filter by (positive/negative/neutral/mixed)
    filter_mode             : Enum__Classification__Filter_Mode                # How to compare ratings (above/below)
    threshold               : Safe_Float                                       # Primary threshold value for filtering
    output_mode             : Enum__Classification__Output_Mode = Enum__Classification__Output_Mode.FULL_RATINGS  # How to format output
