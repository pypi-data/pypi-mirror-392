from osbot_fast_api.api.schemas.consts.consts__Fast_API                                                  import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API                                       import Deploy__Serverless__Fast_API
from osbot_utils.utils.Env                                                                               import get_env
from mgraph_ai_service_semantic_text.config                                                              import SERVICE_NAME, LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS
from mgraph_ai_service_semantic_text.fast_api.lambda_handler                                             import run
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__AWS_Comprehend import ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__BASE_URL, ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME, ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE


class Deploy__Service(Deploy__Serverless__Fast_API):

    def deploy_lambda(self):
        with super().deploy_lambda() as _:
            # Add any service-specific environment variables here
            # Example: _.set_env_variable('BASE_API_KEY', get_env('BASE_API_KEY'))
            _.set_env_variable(ENV_VAR__FAST_API__AUTH__API_KEY__NAME              , get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME             ))
            _.set_env_variable(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE             , get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE            ))
            _.set_env_variable(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__BASE_URL  , get_env(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__BASE_URL ))
            _.set_env_variable(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME  , get_env(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME ))
            _.set_env_variable(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE , get_env(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE))
            return _

    def handler(self):
        return run

    def lambda_dependencies(self):
        return LAMBDA_DEPENDENCIES__FAST_API_SERVERLESS

    def lambda_name(self):
        return SERVICE_NAME