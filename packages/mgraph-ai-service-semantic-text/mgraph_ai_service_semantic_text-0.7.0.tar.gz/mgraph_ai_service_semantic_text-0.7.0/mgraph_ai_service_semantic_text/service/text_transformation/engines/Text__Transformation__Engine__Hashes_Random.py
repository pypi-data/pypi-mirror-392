from typing                                                                                               import Dict, List, Optional
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                             import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                        import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                                     import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                            import type_safe
from mgraph_ai_service_semantic_text.service.text_transformation.engines.Text__Transformation__Engine     import Text__Transformation__Engine
from mgraph_ai_service_semantic_text.schemas.transformation.enums.Enum__Text__Transformation__Mode        import Enum__Text__Transformation__Mode


class Text__Transformation__Engine__Hashes_Random(Text__Transformation__Engine):                            # Randomly replace text with hash values
    transformation_mode : Enum__Text__Transformation__Mode = Enum__Text__Transformation__Mode.HASHES

    @type_safe
    def transform(self,                                                                  # Replace selected hashes with their hash values
                  hash_mapping     : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text],   # Input hash → text mapping
                  selected_hashes  : List[Safe_Str__Hash] = None                         # Hashes to transform
             ) -> Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]:                      # Transformed hash → text mapping
        if not hash_mapping:
            return hash_mapping

        # If no selected_hashes provided, transform none
        hashes_to_transform = set(selected_hashes) if selected_hashes else set() # #set(hash_mapping.keys())
        
        modified_mapping = Type_Safe__Dict(expected_key_type  =  Safe_Str__Hash,
                                           expected_value_type = Safe_Str__Comprehend__Text)


        for hash_key, original_text in hash_mapping.items():
            if hash_key in hashes_to_transform:
                modified_mapping[hash_key] = Safe_Str__Comprehend__Text(hash_key)   # Replace text with hash value itself (converted to Safe_Str__Comprehend__Text)
            else:
                modified_mapping[hash_key] = original_text                          # Keep original text

        return modified_mapping
