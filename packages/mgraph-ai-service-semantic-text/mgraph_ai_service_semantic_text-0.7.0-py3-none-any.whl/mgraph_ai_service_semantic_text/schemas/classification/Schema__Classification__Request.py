from typing                                                                             import Dict
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text           import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash      import Safe_Str__Hash


class Schema__Classification__Request(Type_Safe):                              # Request to classify hash mapping - returns all 4 sentiment scores
    hash_mapping : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]            # Hash → original text mapping
