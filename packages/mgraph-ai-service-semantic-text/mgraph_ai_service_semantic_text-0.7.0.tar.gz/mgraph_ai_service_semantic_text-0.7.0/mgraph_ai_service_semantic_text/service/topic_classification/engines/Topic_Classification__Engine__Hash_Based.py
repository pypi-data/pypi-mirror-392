from hashlib                                                                                           import md5
from typing                                                                                            import Dict, List
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                         import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                           import Safe_Str__Text
from mgraph_ai_service_semantic_text.schemas.topic.enums.Enum__Classification__Topic                   import Enum__Classification__Topic
from mgraph_ai_service_semantic_text.schemas.topic.safe_float.Safe_Float__Topic_Confidence             import Safe_Float__Topic_Confidence
from mgraph_ai_service_semantic_text.service.topic_classification.engines.Topic_Classification__Engine import Topic_Classification__Engine


class Topic_Classification__Engine__Hash_Based(Topic_Classification__Engine):                               # Deterministic hash-based topic classification engine
    
    @type_safe
    def classify_topics(self   ,                                                         # Classify text for multiple topics using deterministic hashing
                        text   : Safe_Str__Text,                                         # Text to classify
                        topics : List[Enum__Classification__Topic]                       # List of Enum__Classification__Topic values
                   ) -> Dict[Enum__Classification__Topic,Safe_Float__Topic_Confidence]:  # Dict[Enum__Classification__Topic → Safe_Float__Topic_Confidence]

        topic_scores = {}
        
        for topic in topics:
            confidence = self.hash_based_confidence(text, topic)
            topic_scores[topic] = confidence
        
        return topic_scores
    
    @type_safe
    def hash_based_confidence(self  ,                                          # Calculate deterministic confidence score using MD5 hash
                              text  : Safe_Str__Text,                          # Text to score
                              topic :Enum__Classification__Topic
                         ) -> Safe_Float__Topic_Confidence:
        combined  = f"{text}_{topic.value}"                                    # Combine text + topic for unique rating per topic
        full_hash = md5(combined.encode()).hexdigest()                         # Get MD5 hash (32 hex characters)
        hash_int  = int(full_hash[:16], 16)                                    # Convert first 16 hex chars (64 bits) to integer
        confidence = (hash_int % 10000) / 10000.0                              # Normalize to 0.0-1.0 range using modulo for even distribution
        
        return Safe_Float__Topic_Confidence(confidence)
