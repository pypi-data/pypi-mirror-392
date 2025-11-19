from typing                                                                          import Dict, List

from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                 import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash   import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                       import type_safe


class Text__Grouping__Service(Type_Safe):                                           # Service for grouping text hashes by various criteria
    num_groups : Safe_UInt = Safe_UInt(5)                                            # Default: 5 groups (a,b,c,d,e)

    @type_safe
    def group_by_length(self,                                                           # Group hashes by text length into N equal-sized buckets
                        hash_mapping: Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]  # Hash → text mapping
                   ) -> Dict[int, List[Safe_Str__Hash]]:                                # Group index → list of hashes
        if not hash_mapping:
            return {}

        hashes_by_length = sorted(hash_mapping.items(), key=lambda x: len(x[1]))
        total_items      = len(hashes_by_length)

        if total_items < int(self.num_groups):
            return {i: [hashes_by_length[i][0]] for i in range(total_items)}

        base_size     = total_items // int(self.num_groups)
        remainder     = total_items % int(self.num_groups)
        groups        = {i: [] for i in range(int(self.num_groups))}
        current_index = 0

        for group_idx in range(int(self.num_groups)):
            group_size = base_size + (1 if group_idx < remainder else 0)

            for _ in range(group_size):
                if current_index < total_items:
                    hash_key, _ = hashes_by_length[current_index]
                    groups[group_idx].append(hash_key)
                    current_index += 1

        return {k: v for k, v in groups.items() if v}

    @type_safe
    def get_group_stats(self,                                                               # Get statistics about each group
                        hash_mapping : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text],    # Hash → text mapping
                        groups       : Dict[int, List[Safe_Str__Hash]]                      # Group index → list of hashes
                       ) -> Dict[int, dict]:                                                # Group index → stats dict
        stats = {}

        for group_idx, hashes in groups.items():
            lengths = [len(hash_mapping[h]) for h in hashes]

            # todo: refactor the dict below into a Type_Safe class
            stats[group_idx] = { "count"       : len(hashes)                                                                                      ,
                                 "min_length"  : min(lengths) if lengths else 0                                                                   ,
                                 "max_length"  : max(lengths) if lengths else 0                                                                   ,
                                 "avg_length"  : sum(lengths) / len(lengths) if lengths else 0                                                    ,
                                 "sample_texts": [hash_mapping[h][:50] + "..." if len(hash_mapping[h]) > 50 else hash_mapping[h]
                                                  for h in hashes[:3]]                                                                            } # First 3 as samples

        return stats

    @type_safe
    def get_group_letter(self,                                                      # Convert group index to letter (0='a', 1='b', etc.)
                         group_index: int
                    ) -> str:                                                       # todo: see if we shouldn't be using an Safe_Str__* class here
        if group_index < 26:
            return chr(ord('a') + group_index)
        else:
            first  = chr(ord('a') + (group_index // 26) - 1)
            second = chr(ord('a') + (group_index % 26))
            return first + second