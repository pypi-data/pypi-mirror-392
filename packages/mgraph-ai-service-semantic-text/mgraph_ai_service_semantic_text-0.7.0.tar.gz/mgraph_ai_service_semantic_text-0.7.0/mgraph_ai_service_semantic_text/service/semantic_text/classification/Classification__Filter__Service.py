from typing                                                                                                         import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                                       import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                                  import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                      import type_safe
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode                          import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria                             import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification                            import Safe_Float__Text__Classification
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Request                         import Schema__Classification__Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Response                        import Schema__Classification__Response
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Filter_Request                  import Schema__Classification__Filter_Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Filter_Response                 import Schema__Classification__Filter_Response
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Output_Mode                 import Enum__Classification__Output_Mode
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Filter_Mode                 import Enum__Classification__Filter_Mode
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Request          import Schema__Classification__Multi_Criteria_Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Response         import Schema__Classification__Multi_Criteria_Response
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Filter_Request   import Schema__Classification__Multi_Criteria_Filter_Request
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Multi_Criteria_Filter_Response  import Schema__Classification__Multi_Criteria_Filter_Response
from mgraph_ai_service_semantic_text.schemas.classification.Schema__Classification__Criterion_Filter                import Schema__Classification__Criterion_Filter
from mgraph_ai_service_semantic_text.schemas.classification.enums.Enum__Classification__Logic_Operator              import Enum__Classification__Logic_Operator
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__Factory                   import Semantic_Text__Engine__Factory


class Classification__Filter__Service(Type_Safe):
    engine_factory : Semantic_Text__Engine__Factory                         # Type_Safe will call Semantic_Text__Engine__Factory() and assigned it to engine_factory

    @type_safe
    def classify_all(self,
                     request    : Schema__Classification__Request        ,
                     engine_mode: Enum__Text__Classification__Engine_Mode
                ) -> Schema__Classification__Response:

        engine  = self.engine_factory.get_engine(engine_mode)

        hash_ratings = {}                                                   # Classify all hashes (returns 4 scores per hash)
        for hash_key, text_value in request.hash_mapping.items():
            scores = engine.classify_text(text_value)                       # Returns all 4 scores
            hash_ratings[hash_key] = scores

        return Schema__Classification__Response(hash_ratings = hash_ratings             ,
                                                total_hashes = len(request.hash_mapping),
                                                success      = True                     )

    @type_safe
    def filter_by_criteria(self,                                                    # Filter hashes based on criteria threshold
                           request    : Schema__Classification__Filter_Request  ,   # Filter request
                           engine_mode: Enum__Text__Classification__Engine_Mode
                      ) -> Schema__Classification__Filter_Response:                 # Filtered results

        classify_request = Schema__Classification__Request(hash_mapping=request.hash_mapping)                           # First, get all classifications


        classify_response = self.classify_all(request     = classify_request,
                                              engine_mode = engine_mode     )

        if not classify_response.success:
            return Schema__Classification__Filter_Response(filtered_hashes         = []                                              ,
                                                           classification_criteria = request.classification_criteria                 ,
                                                           output_mode             = request.output_mode                              ,
                                                           total_hashes            = Safe_UInt(len(request.hash_mapping))             ,
                                                           filtered_count          = Safe_UInt(0)                                     ,
                                                           success                 = False                                            )

        criterion_ratings = {}                                                                  # Extract the specific criterion scores and apply filter
        for hash_key, all_scores in classify_response.hash_ratings.items():
            criterion_ratings[hash_key] = all_scores[request.classification_criteria]           #

        filtered_hashes = self._apply_filter(criterion_ratings                ,
                                             request.filter_mode              ,
                                             request.threshold                )

        # Build response based on output_mode
        return self._build_filter_response(filtered_hashes                ,
                                           request.hash_mapping           ,
                                           classify_response.hash_ratings ,                         # Pass full ratings for FULL_RATINGS mode
                                           request.classification_criteria,
                                           request.output_mode            ,
                                           classify_response.total_hashes )

    @type_safe
    def _apply_filter(self,                                                    # Apply filter logic to ratings
                      hash_ratings  : Dict[Safe_Str__Hash, Safe_Float__Text__Classification],  # Hash → rating mapping
                      filter_mode   : Enum__Classification__Filter_Mode        ,  # Filter comparison mode
                      threshold     : float                                    ,  # Primary threshold value
                 ) -> List[Safe_Str__Hash]:                                    # Filtered hash list
        filtered = []

        for hash_key, rating in hash_ratings.items():
            rating_value = float(rating)

            if filter_mode == Enum__Classification__Filter_Mode.ABOVE:
                if rating_value > threshold:
                    filtered.append(hash_key)

            elif filter_mode == Enum__Classification__Filter_Mode.BELOW:
                if rating_value < threshold:
                    filtered.append(hash_key)

        return filtered

    @type_safe
    def _build_filter_response(self,                                           # Build response based on output mode
                               filtered_hashes          : List[Safe_Str__Hash]                                            ,
                               hash_mapping             : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text                ],
                               hash_ratings             : Dict[Safe_Str__Hash, Dict[Enum__Text__Classification__Criteria  ,
                                                                                    Safe_Float__Text__Classification    ]],
                               classification_criteria  : Enum__Text__Classification__Criteria                            ,
                               output_mode              : Enum__Classification__Output_Mode                               ,
                               total_hashes             : Safe_UInt
                          ) -> Schema__Classification__Filter_Response:        # Complete filter response
        filtered_with_text    = None
        filtered_with_ratings = None

        if output_mode in [Enum__Classification__Output_Mode.HASHES_WITH_TEXT, Enum__Classification__Output_Mode.FULL_RATINGS]:
            filtered_with_text = {h: hash_mapping[h] for h in filtered_hashes if h in hash_mapping}

        if output_mode == Enum__Classification__Output_Mode.FULL_RATINGS:
            filtered_with_ratings = {h: hash_ratings[h] for h in filtered_hashes if h in hash_ratings}

        return Schema__Classification__Filter_Response(filtered_hashes        = filtered_hashes                ,
                                                      filtered_with_text      = filtered_with_text             ,
                                                      filtered_with_ratings   = filtered_with_ratings          ,
                                                      classification_criteria = classification_criteria        ,
                                                      output_mode             = output_mode                    ,
                                                      total_hashes            = total_hashes                   ,
                                                      filtered_count          = Safe_UInt(len(filtered_hashes)),
                                                      success                 = True                           )

    # ========================================
    # Level 2: Multiple Criteria Methods
    # ========================================

    @type_safe
    def classify_all__multi_criteria(self,
                                     request: Schema__Classification__Multi_Criteria_Request,
                                     engine_mode: Enum__Text__Classification__Engine_Mode  # ✅ Add
                                ) -> Schema__Classification__Multi_Criteria_Response:

        engine = self.engine_factory.get_engine(engine_mode)

        hash_ratings = {}
        for hash_key, text_value in request.hash_mapping.items():
            all_scores = engine.classify_text(text_value)
            hash_ratings[hash_key] = all_scores

        return Schema__Classification__Multi_Criteria_Response(hash_ratings = hash_ratings             ,
                                                               total_hashes = len(request.hash_mapping),
                                                               success      = True                     )

    @type_safe
    def filter_by_multi_criteria(self,
                                request    : Schema__Classification__Multi_Criteria_Filter_Request,
                                engine_mode : Enum__Text__Classification__Engine_Mode
                           ) -> Schema__Classification__Multi_Criteria_Filter_Response:

        criteria_list    = [f.criterion for f in request.criterion_filters]                                            # Get all classifications
        classify_request = Schema__Classification__Multi_Criteria_Request(hash_mapping=request.hash_mapping)
        classify_response = self.classify_all__multi_criteria(classify_request, engine_mode)

        if not classify_response.success:
            return Schema__Classification__Multi_Criteria_Filter_Response(filtered_hashes       = []                       ,
                                                                          filtered_with_text    = None                     ,
                                                                          filtered_with_ratings = None                     ,
                                                                          criteria_used         = criteria_list            ,
                                                                          logic_operator        = request.logic_operator   ,
                                                                          output_mode           = request.output_mode      ,
                                                                          total_hashes          = len(request.hash_mapping),
                                                                          filtered_count        = 0                        ,
                                                                          success               = False                    )

        filtered_hashes = self._apply_multi_criteria_filter(classify_response.hash_ratings,             # Apply filters with AND/OR logic
                                                            request.criterion_filters     ,
                                                            request.logic_operator        )

        return self._build_multi_criteria_filter_response(filtered_hashes                   ,           # Build response
                                                          request.hash_mapping              ,
                                                          classify_response.hash_ratings    ,
                                                          criteria_list                     ,
                                                          request.logic_operator            ,
                                                          request.output_mode               ,
                                                          classify_response.total_hashes    )

    @type_safe
    def _apply_multi_criteria_filter(self,                                     # Apply multiple criterion filters with AND/OR logic
                                      hash_ratings      : Dict[Safe_Str__Hash, Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]],
                                      criterion_filters : List[Schema__Classification__Criterion_Filter],
                                      logic_operator    : Enum__Classification__Logic_Operator
                                 ) -> List[Safe_Str__Hash]:                     # Filtered hash list
        if logic_operator == Enum__Classification__Logic_Operator.AND:
            return self._apply_and_filter(hash_ratings, criterion_filters)
        else:  # OR
            return self._apply_or_filter(hash_ratings, criterion_filters)

    @type_safe
    def _apply_and_filter(self,                                                # Apply AND logic - all filters must match
                          hash_ratings      : Dict[Safe_Str__Hash, Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]],
                          criterion_filters : List[Schema__Classification__Criterion_Filter]
                     ) -> List[Safe_Str__Hash]:                                 # Filtered hash list
        filtered = []

        for hash_key, criteria_ratings in hash_ratings.items():
            all_match = True

            for criterion_filter in criterion_filters:
                rating = criteria_ratings.get(criterion_filter.criterion)

                if rating is None:
                    all_match = False
                    break

                rating_value = float(rating)
                matches = self._check_filter_match(rating_value                     ,
                                                   criterion_filter.filter_mode     ,
                                                   float(criterion_filter.threshold))

                if not matches:
                    all_match = False
                    break

            if all_match:
                filtered.append(hash_key)

        return filtered

    @type_safe
    def _apply_or_filter(self,                                                 # Apply OR logic - any filter can match
                         hash_ratings      : Dict[Safe_Str__Hash, Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]],
                         criterion_filters : List[Schema__Classification__Criterion_Filter]
                    ) -> List[Safe_Str__Hash]:                                  # Filtered hash list
        filtered = []

        for hash_key, criteria_ratings in hash_ratings.items():
            any_match = False

            for criterion_filter in criterion_filters:
                rating = criteria_ratings.get(criterion_filter.criterion)

                if rating is None:
                    continue

                rating_value = float(rating)
                matches = self._check_filter_match(rating_value                     ,
                                                   criterion_filter.filter_mode     ,
                                                   float(criterion_filter.threshold))

                if matches:
                    any_match = True
                    break

            if any_match:
                filtered.append(hash_key)

        return filtered

    @type_safe
    def _check_filter_match(self,                                              # Check if rating matches filter condition
                            rating_value  : float                              ,
                            filter_mode   : Enum__Classification__Filter_Mode ,
                            threshold     : float
                       ) -> bool:                                              # Whether rating matches filter
        if filter_mode == Enum__Classification__Filter_Mode.ABOVE:
            return rating_value > threshold

        elif filter_mode == Enum__Classification__Filter_Mode.BELOW:
            return rating_value < threshold

    @type_safe
    def _build_multi_criteria_filter_response(self,                            # Build multi-criteria filter response based on output mode
                                              filtered_hashes  : List[Safe_Str__Hash]                                                          ,
                                              hash_mapping     : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]                                                  ,
                                              hash_ratings     : Dict[Safe_Str__Hash,
                                                                      Dict          [Enum__Text__Classification__Criteria,
                                                                                     Safe_Float__Text__Classification    ]],
                                              criteria_used    : List[Enum__Text__Classification__Criteria]                                    ,
                                              logic_operator   : Enum__Classification__Logic_Operator                                          ,
                                              output_mode      : Enum__Classification__Output_Mode                                             ,
                                              total_hashes     : Safe_UInt
                                         ) -> Schema__Classification__Multi_Criteria_Filter_Response:  # Complete multi-criteria filter response
        filtered_with_text    = None
        filtered_with_ratings = None

        if output_mode in [Enum__Classification__Output_Mode.HASHES_WITH_TEXT, Enum__Classification__Output_Mode.FULL_RATINGS]:
            filtered_with_text = {h: hash_mapping[h] for h in filtered_hashes if h in hash_mapping}

        if output_mode == Enum__Classification__Output_Mode.FULL_RATINGS:
            filtered_with_ratings = {h: hash_ratings[h] for h in filtered_hashes if h in hash_ratings}

        return Schema__Classification__Multi_Criteria_Filter_Response(filtered_hashes     = filtered_hashes           ,
                                                                      filtered_with_text  = filtered_with_text        ,
                                                                      filtered_with_ratings = filtered_with_ratings   ,
                                                                      criteria_used       = criteria_used             ,
                                                                      logic_operator      = logic_operator            ,
                                                                      output_mode         = output_mode               ,
                                                                      total_hashes        = total_hashes              ,
                                                                      filtered_count      = Safe_UInt(len(filtered_hashes)),
                                                                      success             = True                      )
