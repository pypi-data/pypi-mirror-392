from typing                                                                             import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text           import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash      import Safe_Str__Hash

# todo: see if we should not have a better named str class than Safe_Str__Comprehend__Text (one that is relevant to this project)
class Schema__Classification__Multi_Criteria_Request(Type_Safe):               # Request to classify hashes by multiple criteria (returns all 4 always)
    hash_mapping : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]            # Hash → original text mapping
