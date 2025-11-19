from typing                                                                     import List
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text    import Safe_Str__Text


class Topic_Classification__Engine(Type_Safe):                                 # Base class for topic classification engines
    
    def classify_topics(self,                                                  # Classify text for all topics
                        text   : Safe_Str__Text,                               # Text to classify
                        topics : List                                          # List of topics to classify (Enum__Classification__Topic)
                   ):                                                          # Returns Dict[topic → confidence]
        raise NotImplementedError("Subclass must implement classify_topics()")
