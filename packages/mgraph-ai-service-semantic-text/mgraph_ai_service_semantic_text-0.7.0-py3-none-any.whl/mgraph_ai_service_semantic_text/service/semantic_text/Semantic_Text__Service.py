# from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
# from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                            import Safe_Str__Text
# from mgraph_ai_service_semantic_text.schemas.Schema__Semantic_Text__Classification                      import Schema__Semantic_Text__Classification
# from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria                 import Enum__Text__Classification__Criteria
# from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine                import Semantic_Text__Engine
# from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__Hash_Based    import Semantic_Text__Engine__Hash_Based
#
#
# class Semantic_Text__Service(Type_Safe):
#     semantic_text__engine: Semantic_Text__Engine = None
#
#     def setup(self):
#         #self.semantic_text__engine = Semantic_Text__Engine__Random()        # todo: figure out how to assign this (specially when we wire in the multiple LLMs engines)
#         self.semantic_text__engine = Semantic_Text__Engine__Hash_Based()    # Using hash-based engine for deterministic, reproducible classifications   (pseudo random mappings based on the hash value)
#         return self
#
#     def classify_text(self,
#                       text                     : Safe_Str__Text,  # todo: review the use of Safe_Ste__Text (I think it will be too restrictive, specially when we are using non-random data)
#                       classification_criteria  : Enum__Text__Classification__Criteria
#                  ) -> Schema__Semantic_Text__Classification:
#         return self.semantic_text__engine.classify_text(text                     = text,
#                                                         classification_criteria= classification_criteria)