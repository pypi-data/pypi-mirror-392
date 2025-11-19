from osbot_fast_api.api.routes.Routes__Set_Cookie                                    import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API                         import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info                          import Routes__Info
from mgraph_ai_service_semantic_text.config                                          import FAST_API__TITLE
from mgraph_ai_service_semantic_text.fast_api.routes.Routes__Semantic_Classification import Routes__Semantic_Classification
from mgraph_ai_service_semantic_text.fast_api.routes.Routes__Text_Transformation     import Routes__Text_Transformation
from mgraph_ai_service_semantic_text.fast_api.routes.Routes__Topic_Classification    import Routes__Topic_Classification
from mgraph_ai_service_semantic_text.utils.Version                                   import version__mgraph_ai_service_semantic_text



class Semantic_Text__Service__Fast_API(Serverless__Fast_API):
    enable_api_key = False                                           # todo: update to new version of Serverless__Fast_API and use the new config object

    def fast_api__title(self):                                       # todo: move this to the Fast_API class
        return FAST_API__TITLE

    def setup(self):
        super().setup()
        self.setup_fast_api_title_and_version()
        return self

    def setup_fast_api_title_and_version(self):                     # todo: move this to the Fast_API class
        app       = self.app()
        app.title = self.fast_api__title()
        app.version = version__mgraph_ai_service_semantic_text
        return self

    def setup_routes(self):
        self.add_routes(Routes__Info                   )
        self.add_routes(Routes__Text_Transformation    )
        self.add_routes(Routes__Semantic_Classification)
        self.add_routes(Routes__Topic_Classification   )
        self.add_routes(Routes__Set_Cookie             )



