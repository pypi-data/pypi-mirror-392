from fastapi                                                                                                       import HTTPException
from osbot_fast_api.api.decorators.route_path                                                                          import route_path
from osbot_fast_api.api.routes.Fast_API__Routes                                                                        import Fast_API__Routes
from osbot_fast_api.api.schemas.safe_str.Safe_Str__Fast_API__Route__Tag                                                import Safe_Str__Fast_API__Route__Tag
from osbot_utils.type_safe.primitives.core.Safe_Float                                                                  import Safe_Float
from mgraph_ai_service_semantic_text.service.text_transformation.Text__Transformation__Service                         import Text__Transformation__Service
from mgraph_ai_service_semantic_text.schemas.transformation.Schema__Text__Transformation__Request                      import Schema__Text__Transformation__Request
from mgraph_ai_service_semantic_text.schemas.transformation.Schema__Text__Transformation__Request__Path_Params         import Schema__Text__Transformation__Request__Path_Params
from mgraph_ai_service_semantic_text.schemas.transformation.Schema__Text__Transformation__Response                     import Schema__Text__Transformation__Response
from mgraph_ai_service_semantic_text.schemas.transformation.enums.Enum__Text__Transformation__Engine_Mode              import Enum__Text__Transformation__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.transformation.enums.Enum__Text__Transformation__Mode                     import Enum__Text__Transformation__Mode
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria                                import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Filter_Mode                    import Enum__Classification__Filter_Mode
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Logic_Operator                 import Enum__Classification__Logic_Operator
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Criterion_Filter                   import Schema__Classification__Criterion_Filter

TAG__ROUTES_TEXT_TRANSFORMATION   = 'text-transformation'
ROUTES_PATHS__TEXT_TRANSFORMATION = [ f'/{TAG__ROUTES_TEXT_TRANSFORMATION}' + '/transform'                                                                                   ,       # Unified endpoint for multi-criteria
                                      f'/{TAG__ROUTES_TEXT_TRANSFORMATION}' + '/transform/{engine_mode}/{transformation_mode}/{criteria}/{filter_mode}/{threshold}'            ]     # Path params endpoint for single-criterion


class Routes__Text_Transformation(Fast_API__Routes):                                                                   # FastAPI routes for text transformation
    tag     : Safe_Str__Fast_API__Route__Tag    = TAG__ROUTES_TEXT_TRANSFORMATION                                      # OpenAPI tag
    service : Text__Transformation__Service                                                                             # Transformation service

    def transform(self                                      ,                                                           # Transform hash mapping endpoint (unified with filtering support)
                  request: Schema__Text__Transformation__Request                                                        # Transformation request (supports multi-criteria filtering)
             ) -> Schema__Text__Transformation__Response:                                                               # Transformation response

        response = self.service.transform(request)

        if not response.success:        # todo: review this patterns, since we might want to return the response object too
            raise HTTPException(status_code=500, detail=response.error_message)

        return response


    @route_path("/transform/{engine_mode}/{transformation_mode}/{criteria}/{filter_mode}/{threshold}")
    def transform__path_filtered(self,                                                                      # Path Params route for simple single-criterion filtering
                                 engine_mode          : Enum__Text__Transformation__Engine_Mode          ,  # Engine mode (path param): aws_comprehend, text_hash, random
                                 transformation_mode  : Enum__Text__Transformation__Mode                 ,  # Transformation mode (path param): xxx, hashes-random, abcde-by-size
                                 criteria             : Enum__Text__Classification__Criteria             ,  # Single criterion (path param): positive, negative, neutral, mixed
                                 filter_mode          : Enum__Classification__Filter_Mode                ,  # Filter comparison (path param): above, below
                                 threshold            : Safe_Float                                       ,  # Threshold value (path param): 0.0-1.0
                                 request              : Schema__Text__Transformation__Request__Path_Params  # Simplified request body (only hash_mapping required)
                            ) -> Schema__Text__Transformation__Response:                                    # Transformation response

        full_request = self._build_full_request(                                    # Convert Path Params to full request format
            hash_mapping        = request.hash_mapping      ,
            engine_mode         = engine_mode               ,
            transformation_mode = transformation_mode       ,
            criteria            = criteria                  ,
            filter_mode         = filter_mode               ,
            threshold           = threshold
        )

        response = self.service.transform(full_request)                             # Delegate to main transform method

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error_message)

        return response


    def _build_full_request(self                                            ,                                           # Convert path params to full request schema
                           hash_mapping        ,                                                                        # Hash → text mapping from body
                           engine_mode         : Enum__Text__Transformation__Engine_Mode    ,                           # Engine mode from path
                           transformation_mode : Enum__Text__Transformation__Mode           ,                           # Transformation mode from path
                           criteria            : Enum__Text__Classification__Criteria       ,                           # Single criterion from path
                           filter_mode         : Enum__Classification__Filter_Mode          ,                           # Filter mode from path
                           threshold           : Safe_Float                                                             # Threshold from path
                      ) -> Schema__Text__Transformation__Request:                                                       # Full request schema for service

        # Create single criterion filter from path params
        criterion_filter = Schema__Classification__Criterion_Filter(
            criterion   = criteria      ,                                                                               # positive/negative/neutral/mixed
            filter_mode = filter_mode   ,                                                                               # above/below
            threshold   = threshold                                                                                     # 0.0-1.0
        )

        # Build full request
        return Schema__Text__Transformation__Request(
            hash_mapping        = hash_mapping              ,                                                           # From request body
            engine_mode         = engine_mode               ,                                                           # From path param
            criterion_filters   = [criterion_filter]        ,                                                           # Single filter from path params
            logic_operator      = Enum__Classification__Logic_Operator.AND,                                             # Default (single criterion, so AND vs OR doesn't matter)
            transformation_mode = transformation_mode                                                                   # From path param
        )

    def setup_routes(self):                                                                                             # Register all route handlers
        self.add_route_post(self.transform             )                                                                # POST /text-transformation/transform (unified multi-criteria)
        self.add_route_post(self.transform__path_filtered)                                                                # POST /text-transformation/{engine_mode}/{transformation_mode}/{criteria}/{filter_mode}/{threshold}