import random
from typing                                                                          import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text        import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                 import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash   import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                       import type_safe

FLOAT_SELECT_HASHES__RANDOM_PERCENTAGE = 0.5

class Text__Selection__Service(Type_Safe):                                          # Service for randomly selecting hashes for transformation

    @type_safe
    def randomly_select_hashes(self,                                                        # Randomly select hashes for transformation
                               hash_mapping           : Dict[Safe_Str__Hash,
                                                             Safe_Str__Comprehend__Text],   # Full hash mapping
                          ) -> List[Safe_Str__Hash]:                                        # List of selected hash keys
        randomness_percentage = FLOAT_SELECT_HASHES__RANDOM_PERCENTAGE
        all_hashes            = list(hash_mapping.keys())

        if not all_hashes:
            return []

        num_to_select = max(Safe_UInt(1), Safe_UInt(int(len(all_hashes) * float(randomness_percentage))))
        num_to_select = min(int(num_to_select), len(all_hashes))

        return random.sample(all_hashes, num_to_select)