from osbot_utils.type_safe.Type_Safe                                                                     import Type_Safe
from osbot_utils.decorators.methods.cache_on_self                                                        import cache_on_self
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                           import type_safe
from mgraph_ai_service_semantic_text.schemas.enums.Enum__Text__Classification__Engine_Mode               import Enum__Text__Classification__Engine_Mode
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine                 import Semantic_Text__Engine
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__AWS_Comprehend import Semantic_Text__Engine__AWS_Comprehend
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__Hash_Based     import Semantic_Text__Engine__Hash_Based
from mgraph_ai_service_semantic_text.service.semantic_text.engines.Semantic_Text__Engine__Random         import Semantic_Text__Engine__Random


class Semantic_Text__Engine__Factory(Type_Safe):                               # Factory for creating and caching text classification engines

    @cache_on_self
    def engine__aws_comprehend(self):                                           # Get or create AWS Comprehend engine (singleton via @cache_on_self)
        return Semantic_Text__Engine__AWS_Comprehend()                          # Environment validation happens in __init__

    @cache_on_self
    def engine__text_hash(self):                                                # Get or create hash-based engine (singleton via @cache_on_self)


        return Semantic_Text__Engine__Hash_Based()

    @cache_on_self
    def engine__random(self):                                                   # Get or create random engine (singleton via @cache_on_self)
        return Semantic_Text__Engine__Random()

    @type_safe
    def get_engine(self                            ,                            # Get engine instance by mode (routes to appropriate singleton)
                   engine_mode : Enum__Text__Classification__Engine_Mode
              ) -> Semantic_Text__Engine:                                       # Engine instance for classification

        engine_map = { Enum__Text__Classification__Engine_Mode.AWS_COMPREHEND: self.engine__aws_comprehend,
                       Enum__Text__Classification__Engine_Mode.TEXT_HASH     : self.engine__text_hash     ,
                       Enum__Text__Classification__Engine_Mode.RANDOM        : self.engine__random        }

        engine_getter = engine_map.get(engine_mode)

        if engine_getter is None:                                               # Validate engine mode
            supported = [mode.value for mode in engine_map.keys()]
            raise ValueError(f"Unsupported engine mode: '{engine_mode.value}'. "
                             f"Supported modes: {', '.join(supported)}")

        return engine_getter()                                                  # Call cached method to get/create engine