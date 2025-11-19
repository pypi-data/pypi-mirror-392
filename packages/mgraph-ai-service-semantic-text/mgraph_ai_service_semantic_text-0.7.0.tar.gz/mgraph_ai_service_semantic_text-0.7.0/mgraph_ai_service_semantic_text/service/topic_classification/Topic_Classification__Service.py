from typing                                                                                                         import Dict, List
from osbot_utils.type_safe.Type_Safe                                                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                                        import Safe_Str__Text
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe
from mgraph_ai_service_semantic_text.schemas.topic.enums.Enum__Classification__Topic                                import Enum__Classification__Topic
from mgraph_ai_service_semantic_text.schemas.topic.safe_float.Safe_Float__Topic_Confidence                          import Safe_Float__Topic_Confidence
from mgraph_ai_service_semantic_text.service.topic_classification.engines.Topic_Classification__Engine              import Topic_Classification__Engine
from mgraph_ai_service_semantic_text.service.topic_classification.engines.Topic_Classification__Engine__Hash_Based  import Topic_Classification__Engine__Hash_Based


class Topic_Classification__Service(Type_Safe):                                             # Service for classifying text by topics
    topic_engine : Topic_Classification__Engine = None                                      # engine to use

    def setup(self):                                                                        # Initialize with hash-based engine
        self.topic_engine = Topic_Classification__Engine__Hash_Based()                      # Using hash-based engine for deterministic, reproducible classifications
        return self

    @type_safe
    def classify_topics(self,                                                               # Classify text for all specified topics
                        text   : Safe_Str__Text,                                            # Text to classify
                        topics : List[Enum__Classification__Topic]                          # List of Enum__Classification__Topic values
                   ) -> Dict[Enum__Classification__Topic, Safe_Float__Topic_Confidence]:    # Dict[Enum__Classification__Topic → Safe_Float__Topic_Confidence]
        return self.topic_engine.classify_topics(text   = text,
                                                 topics = topics)
