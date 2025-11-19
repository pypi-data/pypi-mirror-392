from typing                                                                        import Dict
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text      import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                               import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash import Safe_Str__Hash


class Schema__Text__Transformation__Request__ABCDE_By_Size(Type_Safe):           # Request for abcde-by-size transformation
    hash_mapping            : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]   # Hash → original text mapping
    num_groups              : Safe_UInt                        = Safe_UInt(5)    # Number of groups (a,b,c,d,e by default)