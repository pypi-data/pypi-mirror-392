from typing                                                                                               import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                             import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.Type_Safe                                                                      import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                        import Safe_Str__Hash
from mgraph_ai_service_semantic_text.schemas.transformation.enums.Enum__Text__Transformation__Mode        import Enum__Text__Transformation__Mode


class Text__Transformation__Engine(Type_Safe):                                          # Base class for text transformation engines
    transformation_mode     : Enum__Text__Transformation__Mode                          # Transformation mode this engine handles

    def transform(self,                                                                 # Transform hash mapping according to engine logic
                       hash_mapping     : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text],   # Input hash → text mapping
                       selected_hashes  : List[Safe_Str__Hash]           = None         # Hashes to transform
                  ) -> Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]:                # Transformed hash → text mapping
        raise NotImplementedError(f"Subclass must implement transform() method")
