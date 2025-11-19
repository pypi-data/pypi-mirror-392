from typing                                                                                             import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                           import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                      import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Criterion_Filter    import Schema__Classification__Criterion_Filter
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode     import Enum__Classification__Output_Mode
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Logic_Operator  import Enum__Classification__Logic_Operator


class Schema__Classification__Multi_Criteria_Filter_Request(Type_Safe):        # Request to filter hashes by multiple classification criteria
    hash_mapping        : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]     # Hash → original text mapping
    criterion_filters   : List[Schema__Classification__Criterion_Filter]       # List of criterion filters to apply
    logic_operator      : Enum__Classification__Logic_Operator                 # How to combine filters (AND/OR)
    output_mode         : Enum__Classification__Output_Mode = Enum__Classification__Output_Mode.FULL_RATINGS  # How to format output
