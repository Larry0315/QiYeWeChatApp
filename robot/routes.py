from aiohttp import web
from aiohttp_swagger import *
from app.wechat.view import WeGroupHandle
from app.wechat.view import WeChatHandle, WeMessageHandle
from app.healthcheck import HealthCheckHandle


def setup_routes(app):
    app.add_routes(
        [
            web.view('/wechat/message', WeMessageHandle),
            web.view('/wechat/chat', WeChatHandle),
            web.view('/wechat/group', WeGroupHandle),
            web.view('/health', HealthCheckHandle)
        ]
    )
    setup_swagger(app, swagger_from_file="example_swagger.yaml")
    # http://ip:port/api/doc
