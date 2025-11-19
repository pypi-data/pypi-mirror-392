from fastapi                                                                                                        import HTTPException
from osbot_fast_api.api.decorators.route_path                                                                       import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                                     import Fast_API__Routes
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag                                             import Safe_Str__Fast_API__Route__Tag
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode                          import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.service.semantic_text.classification.Classification__Filter__Service           import Classification__Filter__Service
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Request                         import Schema__Classification__Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Response                        import Schema__Classification__Response
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Filter_Request                  import Schema__Classification__Filter_Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Filter_Response                 import Schema__Classification__Filter_Response
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Request          import Schema__Classification__Multi_Criteria_Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Response         import Schema__Classification__Multi_Criteria_Response
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Filter_Request   import Schema__Classification__Multi_Criteria_Filter_Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Filter_Response  import Schema__Classification__Multi_Criteria_Filter_Response
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__Factory                   import Semantic_Text__Engine__Factory

TAG__ROUTES_SEMANTIC_CLASSIFICATION = 'semantic-classification'
ROUTES_PATHS__SEMANTIC_CLASSIFICATION = [    f'/{TAG__ROUTES_SEMANTIC_CLASSIFICATION}' + '/{engine_mode}/rate'          ,
                                             f'/{TAG__ROUTES_SEMANTIC_CLASSIFICATION}' + '/{engine_mode}/filter'        ,
                                             f'/{TAG__ROUTES_SEMANTIC_CLASSIFICATION}' + '/{engine_mode}/multi/rate'    ,
                                             f'/{TAG__ROUTES_SEMANTIC_CLASSIFICATION}' + '/{engine_mode}/multi/filter'  ]

class Routes__Semantic_Classification(Fast_API__Routes):
    tag                    : Safe_Str__Fast_API__Route__Tag = TAG__ROUTES_SEMANTIC_CLASSIFICATION
    classification_service : Classification__Filter__Service
    engine_factory         : Semantic_Text__Engine__Factory

    @route_path("/{engine_mode}/rate")
    def engine_mode__rate(self,
                          engine_mode: Enum__Text__Classification__Engine_Mode,                 # Path param
                          request: Schema__Classification__Request
                     ) -> Schema__Classification__Response:

        response = self.classification_service.classify_all(request, engine_mode)

        if not response.success:
            raise HTTPException(status_code=500, detail="Classification failed")

        return response

    @route_path("/{engine_mode}/filter")
    def engine_mode__filter(self,
                            engine_mode: Enum__Text__Classification__Engine_Mode,              # Path param
                            request    : Schema__Classification__Filter_Request
                       ) -> Schema__Classification__Filter_Response:

        response = self.classification_service.filter_by_criteria(request, engine_mode)

        if not response.success:
            raise HTTPException(status_code=500, detail="Filter failed")

        return response


    # ========================================
    # Level 2: Multiple Criteria
    # ========================================
    @route_path("/{engine_mode}/multi/rate")
    def engine_mode__multi__rate(self,                                                               # Rate all hashes by multiple criteria
                                 engine_mode: Enum__Text__Classification__Engine_Mode,               # Engine to use
                                 request: Schema__Classification__Multi_Criteria_Request
                            ) -> Schema__Classification__Multi_Criteria_Response:

        response = self.classification_service.classify_all__multi_criteria(request, engine_mode)

        if not response.success:
            raise HTTPException(status_code=500, detail="Multi-criteria classification failed")

        return response

    @route_path("/{engine_mode}/multi/filter")
    def engine_mode__multi__filter(self,                                                             # Filter hashes by multiple criteria with AND/OR logic
                                   engine_mode: Enum__Text__Classification__Engine_Mode         ,    # Engine to use
                                   request: Schema__Classification__Multi_Criteria_Filter_Request
                              ) -> Schema__Classification__Multi_Criteria_Filter_Response:

        response = self.classification_service.filter_by_multi_criteria(request, engine_mode)

        if not response.success:
            raise HTTPException(status_code=500, detail="Multi-criteria filter failed")

        return response

    def setup_routes(self):                                                    # Register all route handlers
        self.add_route_post(self.engine_mode__rate          )                  # Rate endpoint
        self.add_route_post(self.engine_mode__filter        )                  # Filter endpoint
        self.add_route_post(self.engine_mode__multi__rate   )                  # Multi-criteria rate endpoint
        self.add_route_post(self.engine_mode__multi__filter )                  # Multi-criteria filter endpoint
