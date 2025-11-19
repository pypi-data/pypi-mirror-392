from typing                                                                                                 import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                               import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                        import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                          import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                              import type_safe
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Logic_Operator      import Enum__Classification__Logic_Operator
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode         import Enum__Classification__Output_Mode
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Classification__Request                    import Schema__Topic_Classification__Request
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Classification__Response                   import Schema__Topic_Classification__Response
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Filter__Request                            import Schema__Topic_Filter__Request
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Filter__Response                           import Schema__Topic_Filter__Response
from mgraph_ai_service_semantic_text.schemas.topic.enums.Enum__Classification__Topic                        import Enum__Classification__Topic
from mgraph_ai_service_semantic_text.schemas.topic.safe_float.Safe_Float__Topic_Confidence                  import Safe_Float__Topic_Confidence
from mgraph_ai_service_semantic_text.service.topic_classification.Topic_Classification__Service             import Topic_Classification__Service


class Topic_Classification__Filter__Service(Type_Safe):                        # Service for filtering hashes based on topic classification
    topic_service           : Topic_Classification__Service = None             # topic classification service
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.topic_service = Topic_Classification__Service().setup()           # Initialize with hash-based engine
    
    @type_safe
    def classify_all(self,                                                     # Classify all hashes for specified topics
                     request : Schema__Topic_Classification__Request           # request data
                ) -> Schema__Topic_Classification__Response:                   # returns topics classification for hash_mappings provided

        hash_topic_scores = {}
        
        for hash_key, text_value in request.hash_mapping.items():
            topic_scores = self.topic_service.classify_topics(text   = text_value,
                                                              topics = request.topics)
            
            # Filter by min_confidence threshold
            filtered_scores = {}
            for topic, confidence in topic_scores.items():
                if float(confidence) >= float(request.min_confidence):
                    filtered_scores[topic] = confidence
            
            if filtered_scores:                                                # Only include hashes that have at least one topic above threshold
                hash_topic_scores[hash_key] = filtered_scores
        
        return Schema__Topic_Classification__Response(hash_topic_scores  = hash_topic_scores                   ,
                                                      topics_classified  = request.topics                      ,
                                                      total_hashes       = Safe_UInt(len(request.hash_mapping)),
                                                      success            = True                                )
    
    @type_safe
    def filter_by_topics(self,                                                 # Filter hashes based on required topics with AND/OR logic
                         request : Schema__Topic_Filter__Request
                    ) -> Schema__Topic_Filter__Response:

        classify_request = Schema__Topic_Classification__Request(hash_mapping    = request.hash_mapping    ,            # First, classify all hashes for required topics
                                                                 topics          = request.required_topics ,
                                                                 min_confidence  = request.min_confidence  )
        
        classify_response = self.classify_all(classify_request)
        
        if not classify_response.success:
            return Schema__Topic_Filter__Response(filtered_hashes  = []                                 ,
                                                 topics_used      = request.required_topics             ,
                                                 logic_operator   = request.logic_operator              ,
                                                 output_mode      = request.output_mode                 ,
                                                 total_hashes     = Safe_UInt(len(request.hash_mapping)),
                                                 filtered_count   = Safe_UInt(0)                        ,
                                                 success          = False                               )
        
        # Apply AND/OR logic to filter
        filtered_hashes = self._apply_logic_operator(classify_response.hash_topic_scores,
                                                     request.required_topics            ,
                                                     request.logic_operator             ,
                                                     request.min_confidence             )
        
        # Build response based on output_mode
        return self._build_filter_response(filtered_hashes                    ,
                                           request.hash_mapping                ,
                                           classify_response.hash_topic_scores ,
                                           request.required_topics             ,
                                           request.logic_operator              ,
                                           request.output_mode                 ,
                                           classify_response.total_hashes      )
    
    @type_safe
    def _apply_logic_operator(self,                                                         # Apply AND/OR logic to filter hashes by topics
                              hash_topic_scores : Dict[Safe_Str__Hash, Dict]          ,     # Hash → {topic → confidence}
                              required_topics   : List[Enum__Classification__Topic]   ,     # List of topics
                              logic_operator    : Enum__Classification__Logic_Operator,
                              min_confidence    : Safe_Float__Topic_Confidence
                         ) -> List[Safe_Str__Hash]:                            # List of filtered hashes

        
        filtered = []
        
        for hash_key, topic_scores in hash_topic_scores.items():
            if logic_operator == Enum__Classification__Logic_Operator.AND:
                all_match = all(topic in topic_scores and float(topic_scores[topic]) >= min_confidence      # ALL required topics must be present and above threshold
                                for topic in required_topics                                          )
                if all_match:
                    filtered.append(hash_key)
            
            else:  # OR
                any_match = any(topic in topic_scores and float(topic_scores[topic]) >= min_confidence      # ANY required topic must be present and above threshold
                                for topic in required_topics                                         )
                if any_match:
                    filtered.append(hash_key)
        
        return filtered
    
    @type_safe
    def _build_filter_response(self,                                                                    # Build filter response based on output mode
                               filtered_hashes      : List[Safe_Str__Hash]                             ,
                               hash_mapping         : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text] ,
                               hash_topic_scores    : Dict[Safe_Str__Hash, Dict]                       ,
                               required_topics      : List[Enum__Classification__Topic]                ,
                               logic_operator       : Enum__Classification__Logic_Operator             ,
                               output_mode          : Enum__Classification__Output_Mode                ,
                               total_hashes         : Safe_UInt
                          ) -> Schema__Topic_Filter__Response:

        
        filtered_with_text   = None
        filtered_with_scores = None
        
        if output_mode in [Enum__Classification__Output_Mode.HASHES_WITH_TEXT, Enum__Classification__Output_Mode.FULL_RATINGS]:
            filtered_with_text = {h: hash_mapping[h] for h in filtered_hashes if h in hash_mapping}
        
        if output_mode == Enum__Classification__Output_Mode.FULL_RATINGS:
            filtered_with_scores = {h: hash_topic_scores[h] for h in filtered_hashes if h in hash_topic_scores}
        
        return Schema__Topic_Filter__Response(filtered_hashes      = filtered_hashes                 ,
                                              filtered_with_text   = filtered_with_text             ,
                                              filtered_with_scores = filtered_with_scores          ,
                                              topics_used          = required_topics                ,
                                              logic_operator       = logic_operator                 ,
                                              output_mode          = output_mode                    ,
                                              total_hashes         = total_hashes                   ,
                                              filtered_count       = Safe_UInt(len(filtered_hashes)),
                                              success              = True                           )
