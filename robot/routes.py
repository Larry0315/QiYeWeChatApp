from aiohttp import web
from aiohttp_swagger import *
from app.wechat.view import WeGroupHandle
from app.wechat.view import WeChatHandle, WeMessageHandle


def setup_routes(app):
    app.add_routes(
        [
            web.view('/wechat/message', WeMessageHandle),
            web.view('/wechat/chat', WeChatHandle),
            web.view('/wechat/group', WeGroupHandle),
        ]
    )
    setup_swagger(app, swagger_from_file="example_swagger.yaml")
    # http://ip:port/api/doc
