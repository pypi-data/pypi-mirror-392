import requests
from typing                                                                                     import Dict
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                  import type_safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                    import Safe_Str__Text
from osbot_utils.utils.Env                                                                      import get_env
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Criteria         import Enum__Text__Classification__Criteria
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode      import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.schemas.safe_float.Safe_Float__Text__Classification        import Safe_Float__Text__Classification
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine        import Semantic_Text__Engine


ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__BASE_URL  = "AUTH__SERVICE__AWS__COMPREHEND__BASE_URL"   # Base URL for AWS Comprehend service
ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME  = "AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME"   # API key header name
ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE = "AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE"  # API key value


class Semantic_Text__Engine__AWS_Comprehend(Semantic_Text__Engine):            # AWS Comprehend ML-based sentiment analysis engine
    engine_mode : Enum__Text__Classification__Engine_Mode = Enum__Text__Classification__Engine_Mode.AWS_COMPREHEND  # AWS Comprehend mode
    base_url    : str                                      = None              # Base URL for Comprehend service (from env var)
    api_key_name: str                                      = None              # API key header name (from env var)
    api_key     : str                                      = None              # API key value (from env var)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_config()                                                     # Load configuration from environment variables

    def _load_config(self):                                                     # Load AWS Comprehend service configuration from environment
        self.base_url     = get_env(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__BASE_URL )
        self.api_key_name = get_env(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME )
        self.api_key      = get_env(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE)

        if not all([self.base_url, self.api_key_name, self.api_key]):          # Validate required environment variables
            missing = []
            if not self.base_url    : missing.append(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__BASE_URL )
            if not self.api_key_name: missing.append(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_NAME )
            if not self.api_key     : missing.append(ENV_NAME__AUTH__SERVICE__AWS__COMPREHEND__KEY_VALUE)

            raise ValueError(f"Missing required environment variables for AWS Comprehend: {', '.join(missing)}")

    @type_safe
    def classify_text(self                 ,                                   # Call AWS Comprehend API for sentiment analysis
                      text : Safe_Str__Text
                 ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:  # All 4 sentiment scores from AWS

        sentiment_result = self._call_comprehend_api(text)                     # Call AWS Comprehend service

        scores = self._map_comprehend_response(sentiment_result)               # Map response to our schema

        return scores

    @type_safe
    def _call_comprehend_api(self         ,                                    # Make HTTP POST request to AWS Comprehend service
                             text : Safe_Str__Text
                        ) -> Dict:                                              # Raw API response

        url     = f"{self.base_url}/comprehend/detect-sentiment"               # Endpoint for sentiment detection
        headers = {self.api_key_name: self.api_key,                            # Authentication header
                   "Content-Type"   : "application/json"}
        payload = {"text"         : str(text)     ,                            # Request body
                   "language_code": "en"          ,
                   "use_cache"    : False         }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()                                         # Raise exception for 4xx/5xx status codes
            return response.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"AWS Comprehend API request failed: {str(e)}")

    @type_safe
    def _map_comprehend_response(self                    ,                     # Map AWS Comprehend response to our classification schema
                                 comprehend_result : Dict
                            ) -> Dict[Enum__Text__Classification__Criteria, Safe_Float__Text__Classification]:  # Mapped scores

        score_data = comprehend_result.get("score", {})                        # Extract score object from response

        scores = {
            Enum__Text__Classification__Criteria.POSITIVE: Safe_Float__Text__Classification(score_data.get("positive", 0.0)),
            Enum__Text__Classification__Criteria.NEGATIVE: Safe_Float__Text__Classification(score_data.get("negative", 0.0)),
            Enum__Text__Classification__Criteria.NEUTRAL : Safe_Float__Text__Classification(score_data.get("neutral" , 0.0)),
            Enum__Text__Classification__Criteria.MIXED   : Safe_Float__Text__Classification(score_data.get("mixed"   , 0.0))
        }

        return scores
