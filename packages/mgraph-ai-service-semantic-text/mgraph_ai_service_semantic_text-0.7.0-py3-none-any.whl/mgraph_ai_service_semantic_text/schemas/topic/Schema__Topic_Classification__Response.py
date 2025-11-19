from typing                                                                          import Dict, List
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                 import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash   import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.topic.enums.Enum__Classification__Topic import Enum__Classification__Topic


class Schema__Topic_Classification__Response(Type_Safe):                       # Response with topic confidence scores for all hashes
    hash_topic_scores       : Dict[Safe_Str__Hash, Dict]                       # Hash → {topic → confidence} mapping
    topics_classified       : List[Enum__Classification__Topic]                # List of topics used
    total_hashes            : Safe_UInt                                        # Total number of hashes classified
    success                 : bool                                             # Whether classification succeeded
