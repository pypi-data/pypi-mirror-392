from typing                                                                                                           import Dict, List, Optional
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                                         import Safe_Str__Comprehend__Text
from osbot_utils.decorators.methods.cache_on_self                                                                     import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                                                  import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                                  import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                                    import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                        import type_safe
from osbot_utils.utils.Misc                                                                                           import list_set
from mgraph_ai_service_semantic_text.service.semantic_text.classification.Classification__Filter__Service             import Classification__Filter__Service
from mgraph_ai_service_semantic_text.service.text_transformation.Text__Grouping__Service                              import Text__Grouping__Service
from mgraph_ai_service_semantic_text.service.text_transformation.engines.Text__Transformation__Engine                 import Text__Transformation__Engine
from mgraph_ai_service_semantic_text.service.text_transformation.engines.Text__Transformation__Engine__XXX_Random     import Text__Transformation__Engine__XXX_Random
from mgraph_ai_service_semantic_text.service.text_transformation.engines.Text__Transformation__Engine__Hashes_Random  import Text__Transformation__Engine__Hashes_Random
from mgraph_ai_service_semantic_text.service.text_transformation.engines.Text__Transformation__Engine__ABCDE_By_Size  import Text__Transformation__Engine__ABCDE_By_Size
from mgraph_ai_service_semantic_text.schemas.transformation.Schema__Text__Transformation__Request                     import Schema__Text__Transformation__Request
from mgraph_ai_service_semantic_text.schemas.transformation.Schema__Text__Transformation__Response                    import Schema__Text__Transformation__Response
from mgraph_ai_service_semantic_text.schemas.transformation.enums.Enum__Text__Transformation__Mode                    import Enum__Text__Transformation__Mode
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Filter_Request     import Schema__Classification__Multi_Criteria_Filter_Request
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode                   import Enum__Classification__Output_Mode


class Text__Transformation__Service(Type_Safe):                                     # Main orchestrator for text transformations with sentiment filtering
    classification_service : Classification__Filter__Service                        # Service for classification and filtering
    text_grouping          : Text__Grouping__Service                                # Service for grouping text by criteria
    engine__xxx_random     : Text__Transformation__Engine__XXX_Random               # Engine for xxx mode
    engine__hashes_random  : Text__Transformation__Engine__Hashes_Random            # Engine for hashes-random mode
    engine__abcde_by_size  : Text__Transformation__Engine__ABCDE_By_Size            # Engine for abcde-by-size mode

    def setup(self) -> 'Text__Transformation__Service':                            # Initialize all engines with shared services
        self.engine__abcde_by_size.text_grouping  = self.text_grouping
        self.engine__abcde_by_size.setup()
        return self

    @type_safe
    def transform(self,                                                             # Transform hash mapping according to request (two-phase operation)
                  request: Schema__Text__Transformation__Request                    # Transformation request
             ) -> Schema__Text__Transformation__Response:                           # Transformation response
        try:
            # Special case: ABCDE mode ALWAYS transforms all, ignores filters
            if request.transformation_mode == Enum__Text__Transformation__Mode.ABCDE_BY_SIZE:
                return self._transform_abcde_all(request)
            
            # Phase 1: Classification & Selection (if filters provided)
            selected_hashes = self._apply_filters(request)
            
            # Phase 2: Visual Transformation
            engine                       = self._get_engine(request.transformation_mode)
            transformed_mapping          = engine.transform(request.hash_mapping, selected_hashes)
            total_hashes                 = len(request.hash_mapping)
            transformed_hashes           = self._count_transformed_hashes(request.hash_mapping, transformed_mapping)

            return Schema__Text__Transformation__Response(transformed_mapping = transformed_mapping         ,
                                                          transformation_mode = request.transformation_mode ,
                                                          success             = True                        ,
                                                          total_hashes        = total_hashes                ,
                                                          transformed_hashes  = transformed_hashes          )

        except Exception as e:
            return Schema__Text__Transformation__Response(transformed_mapping = request.hash_mapping                 ,
                                                          transformation_mode = request.transformation_mode          ,
                                                          success             = False                                ,
                                                          total_hashes        = Safe_UInt(len(request.hash_mapping)) ,
                                                          transformed_hashes  = Safe_UInt(0)                         ,
                                                          error_message       = f"Transformation failed: {str(e)}"   )

    @type_safe
    def _apply_filters(self,                                                        # Phase 1: Apply classification filters to select hashes
                       request: Schema__Text__Transformation__Request               # Transformation request
                  ) -> List[Safe_Str__Hash]:                                        # List of selected hashes (None = all)
        
        # If no engine_mode or no filters, return all
        if request.engine_mode is None or not request.criterion_filters:
            return list_set(request.hash_mapping)
        
        # Build classification filter request
        filter_request = Schema__Classification__Multi_Criteria_Filter_Request(
            hash_mapping        = request.hash_mapping      ,
            criterion_filters   = request.criterion_filters ,
            logic_operator      = request.logic_operator    ,
            output_mode         = Enum__Classification__Output_Mode.HASHES_ONLY             # todo: see if we need to add support from controlling the output mode from the request params
        )
        
        # Call classification service to filter
        filter_response = self.classification_service.filter_by_multi_criteria(filter_request   ,
                                                                                request.engine_mode)
        
        if not filter_response.success:
            raise RuntimeError(f"Classification filtering failed")
        
        # Return filtered hash list (or None if empty)
        return filter_response.filtered_hashes if filter_response.filtered_hashes else None

    @type_safe
    def _transform_abcde_all(self,                                                  # Special handling for ABCDE mode (always transforms all)
                             request: Schema__Text__Transformation__Request         # Transformation request
                        ) -> Schema__Text__Transformation__Response:                # Transformation response
        
        engine              = self.engine__abcde_by_size
        transformed_mapping = engine.transform(request.hash_mapping, selected_hashes=None)  # None signals "transform all"
        total_hashes        = Safe_UInt(len(request.hash_mapping))
        
        return Schema__Text__Transformation__Response(transformed_mapping = transformed_mapping         ,
                                                      transformation_mode = request.transformation_mode ,
                                                      success             = True                        ,
                                                      total_hashes        = total_hashes                ,
                                                      transformed_hashes  = total_hashes                )  # ABCDE transforms all

    @cache_on_self
    @type_safe
    def _get_engine(self,                                                           # Get transformation engine for mode
                    mode: Enum__Text__Transformation__Mode                          # Transformation mode
               ) -> Text__Transformation__Engine:                                   # Transformation engine
        engines = { Enum__Text__Transformation__Mode.XXX    : self.engine__xxx_random    ,
                    Enum__Text__Transformation__Mode.HASHES : self.engine__hashes_random ,
                    Enum__Text__Transformation__Mode.ABCDE_BY_SIZE : self.engine__abcde_by_size }

        engine = engines.get(mode)
        if not engine:
            raise ValueError(f"Unknown transformation mode: {mode}")

        return engine

    @type_safe
    def _count_transformed_hashes(self,                                                                     # Count how many hashes were actually transformed
                                  original_mapping    : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text],   # Original hash mapping
                                  transformed_mapping : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]    # Transformed hash mapping
                             ) -> Safe_UInt:                                                                # Number of transformed hashes
        count = 0
        for hash_key, original_text in original_mapping.items():
            if hash_key in transformed_mapping and transformed_mapping[hash_key] != original_text:
                count += 1
        return count
