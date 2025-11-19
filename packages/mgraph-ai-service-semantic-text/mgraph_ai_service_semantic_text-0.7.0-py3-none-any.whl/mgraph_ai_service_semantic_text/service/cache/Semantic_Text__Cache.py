from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client           import Service__Fast_API__Client
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client__Config   import Service__Fast_API__Client__Config
from mgraph_ai_service_cache_client.schemas.consts.consts__Cache_Client                 import ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE, ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME, ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE
from mgraph_ai_service_semantic_text.utils.Version                                      import version__mgraph_ai_service_semantic_text
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.utils.Env                                                              import get_env

class Semantic_Text__Cache(Type_Safe):
    cache_client : Service__Fast_API__Client = None

    def setup(self):
        self.setup__service_auth()
        return self

    # todo: move this code to mgraph_ai_service_cache_client project
    def setup__service_auth(self):
        base_url          = get_env(ENV_VAR__URL__TARGET_SERVER__CACHE_SERVICE            )
        key_name          = get_env(ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_NAME )
        key_value         = get_env(ENV_VAR__AUTH__TARGET_SERVER__CACHE_SERVICE__KEY_VALUE)
        auth__kwargs      = dict(base_url       = base_url                                 ,
                                 api_key        = key_value                                ,
                                 api_key_header = key_name                                 ,
                                 service_version = version__mgraph_ai_service_semantic_text)        # todo: see if this is the correct use of service_version (and the implications of this value being hardcoded at the moment in Service__Fast_API__Client__Config)
        cache_config      = Service__Fast_API__Client__Config(**auth__kwargs)
        self.cache_client = Service__Fast_API__Client        (config=cache_config)
        return self

    def admin__storage_folders(self, path: str=None):
        return self.cache_client.admin_storage().folders(path=path)

    def server__storage_info(self):
        return self.cache_client.server().storage__info()

    def namespaces(self):
        return self.cache_client.admin_storage().folders(path='/')

