from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text        import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__Hash  import Safe_Str__Hash
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                      import type_safe
from osbot_utils.utils.Misc                                                         import str_md5


class Semantic_Text__Hashes(Type_Safe):
    hash_size : Safe_UInt = 10

    @type_safe
    def hash__for_text(self, text_value: Safe_Str__Text) -> Safe_Str__Hash:
        hash_value  =  str_md5(text_value)[:self.hash_size]                       # todo: replace this with the Cache__Hash__Generator which is available on the Cache_Service  (which should be available in this project)
        return Safe_Str__Hash(hash_value)