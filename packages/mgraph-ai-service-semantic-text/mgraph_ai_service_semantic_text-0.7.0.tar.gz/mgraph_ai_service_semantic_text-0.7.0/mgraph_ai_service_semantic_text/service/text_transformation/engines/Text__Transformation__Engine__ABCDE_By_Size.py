from typing                                                                                               import Dict, List
from osbot_aws.aws.comprehend.schemas.safe_str.Safe_Str__AWS_Comprehend__Text                             import Safe_Str__Comprehend__Text
from osbot_utils.type_safe.primitives.core.Safe_UInt                                                      import Safe_UInt
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash                        import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                                     import Type_Safe__Dict
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                            import type_safe
from mgraph_ai_service_semantic_text.service.text_transformation.engines.Text__Transformation__Engine     import Text__Transformation__Engine
from mgraph_ai_service_semantic_text.service.text_transformation.Text__Grouping__Service                  import Text__Grouping__Service
from mgraph_ai_service_semantic_text.schemas.transformation.enums.Enum__Text__Transformation__Mode        import Enum__Text__Transformation__Mode


class Text__Transformation__Engine__ABCDE_By_Size(Text__Transformation__Engine):    # Group text by size, replace with letters
    transformation_mode : Enum__Text__Transformation__Mode = Enum__Text__Transformation__Mode.ABCDE_BY_SIZE
    text_grouping       : Text__Grouping__Service                                   # Service for grouping by length
    num_groups          : Safe_UInt                         = Safe_UInt(5)          # Number of groups (a,b,c,d,e)

    def setup(self) -> 'Text__Transformation__Engine__ABCDE_By_Size':              # Setup grouping service with num_groups
        self.text_grouping.num_groups = self.num_groups
        return self

    @type_safe
    def transform(self,                                                             # Group text by length, replace with letters (a-e) - ALWAYS transforms ALL
                  hash_mapping     : Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text],   # Input hash → text mapping
                  selected_hashes  : List[Safe_Str__Hash]           = None          # IGNORED - ABCDE always transforms all hashes
             ) -> Dict[Safe_Str__Hash, Safe_Str__Comprehend__Text]:                 # Transformed hash → text mapping
        if not hash_mapping:
            return hash_mapping

        # ABCDE mode ALWAYS transforms ALL hashes - selected_hashes parameter is ignored
        groups           = self.text_grouping.group_by_length(hash_mapping)
        modified_mapping = Type_Safe__Dict(expected_key_type  =  Safe_Str__Hash,
                                           expected_value_type = Safe_Str__Comprehend__Text)


        for group_index, hashes in groups.items():
            group_letter = self.text_grouping.get_group_letter(group_index)

            for hash_key in hashes:
                original_text                = hash_mapping[hash_key]
                modified_mapping[hash_key]   = self._replace_with_letter(original_text, group_letter)

        return modified_mapping

    @type_safe
    def _replace_with_letter(self, text: str, letter: str) -> str:                 # Replace text with repeated letter while preserving structure
        if not text:
            return text

        result = []
        for char in text:
            if char.isalnum():
                result.append(letter)
            elif char.isspace():
                result.append(' ')                                                  # Keep whitespace for word boundaries
            else:
                result.append(char)                                                 # Keep punctuation for readability

        return ''.join(result)
