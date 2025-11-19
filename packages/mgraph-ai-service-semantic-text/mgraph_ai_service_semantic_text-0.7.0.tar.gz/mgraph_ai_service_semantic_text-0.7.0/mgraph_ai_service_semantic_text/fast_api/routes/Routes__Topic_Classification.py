from fastapi                                                                                            import HTTPException
from osbot_fast_api.api.routes.Fast_API__Routes                                                         import Fast_API__Routes
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag                                 import Safe_Str__Fast_API__Route__Tag
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Classification__Request                import Schema__Topic_Classification__Request
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Classification__Response               import Schema__Topic_Classification__Response
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Filter__Request                        import Schema__Topic_Filter__Request
from mgraph_ai_service_semantic_text.schemas.topic.Schema__Topic_Filter__Response                       import Schema__Topic_Filter__Response
from mgraph_ai_service_semantic_text.service.topic_classification.Topic_Classification__Filter__Service import Topic_Classification__Filter__Service

TAG__ROUTES_TOPIC_CLASSIFICATION   = 'topic-classification'
ROUTES_PATHS__TOPIC_CLASSIFICATION = [f'/{TAG__ROUTES_TOPIC_CLASSIFICATION}' + '/classify',    # Classify all topics
                                     f'/{TAG__ROUTES_TOPIC_CLASSIFICATION}' + '/filter'    ]   # Filter by topics


class Routes__Topic_Classification(Fast_API__Routes):                                                             # FastAPI routes for topic classification
    tag                                 : Safe_Str__Fast_API__Route__Tag    = TAG__ROUTES_TOPIC_CLASSIFICATION    # OpenAPI tag
    topic_classification_filter_service : Topic_Classification__Filter__Service                                                                    #  - typed as None
    
    def classify(self,                                                         # Classify all hashes by specified topics
                 request : Schema__Topic_Classification__Request
            ) -> Schema__Topic_Classification__Response:
        response = self.topic_classification_filter_service.classify_all(request)
        
        if not response.success:
            raise HTTPException(status_code=500, detail="Topic classification failed")
        
        return response
    
    def filter(self,                                                           # Filter hashes by topic criteria with AND/OR logic
               request : Schema__Topic_Filter__Request
          ) -> Schema__Topic_Filter__Response:
        
        response = self.topic_classification_filter_service.filter_by_topics(request)
        
        if not response.success:
            raise HTTPException(status_code=500, detail="Topic filtering failed")
        
        return response
    
    def setup_routes(self):                                                    # Register all route handlers
        self.add_route_post(self.classify)                                     # POST /topic-classification/classify
        self.add_route_post(self.filter  )                                     # POST /topic-classification/filter
