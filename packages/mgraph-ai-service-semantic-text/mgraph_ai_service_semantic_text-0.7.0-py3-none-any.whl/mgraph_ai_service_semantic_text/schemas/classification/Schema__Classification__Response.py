from typing                                                                              import Dict
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                     import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash       import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria  import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification import Safe_Float__Text__Classification


class Schema__Classification__Response(Type_Safe):                                      # Response with all 4 classification scores for each hash
    hash_ratings : Dict[Safe_Str__Hash, Dict[Enum__Text__Classification__Criteria,
                                             Safe_Float__Text__Classification    ]]      # Hash → {criterion → score} mapping (all 4 scores)
    total_hashes : Safe_UInt                                                             # Total number of hashes classified
    success      : bool                                                                  # Whether classification succeeded
