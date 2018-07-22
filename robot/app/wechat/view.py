import json
from aiohttp import web
from multidict import MultiDictProxy
from app.wechat.service import WeChatService, \
    ChatGroup, MessageService
from app.wechat.module import WeMessageModule


class WeChatHandle(web.View):
    """
    企业微信信息交互类
    """
    async def get(self):
        """
        用于与企业微信建立连接的认证方法
        :return: 解密后的明文字符串
        """
        # 获取URL中的参数
        data: MultiDictProxy = self.request.query
        msg_sig = data.get('msg_signature')
        timestamp = data.get('timestamp')
        nonce = data.get('nonce')
        echo = data.get('echostr')
        print(msg_sig, timestamp, nonce, echo)

        # 解密
        echo_str = WeChatService().echo(msg_sig, timestamp, nonce, echo)
        print(echo_str)
        # 将解密后的明文字符串发回给企业微信端
        return web.Response(text=echo_str)

    async def post(self):
        """
        用于接收企业微信消息(目前仅响应消息事件, 菜单点击事件将被忽略)
        :return: 回复给用户的密文消息
        """
        # 获取URL中的参数
        data: MultiDictProxy = self.request.query
        msg_sig = data.get('msg_signature')
        timestamp = data.get('timestamp')
        nonce = data.get('nonce')
        # 获取Post body体内容
        req_data: str = await self.request.text()

        # 对企业微信发来的用户消息进行解密
        msg = WeChatService().decode_body(req_data, msg_sig, timestamp, nonce)
        # 对用户请求的内容进行响应体的构建(rep_body为静态方法, 可以用类名直接调用)
        rep_xml_data = await WeChatService.rep_body(msg)
        # 对响应体进行加密
        encrypt_msg = WeChatService().encode_body(rep_xml_data, nonce, timestamp)

        # 最后将密文回复给企业微信，即完成企业微信用户与企业自己服务器之间的信息交互
        return web.Response(text=encrypt_msg)


class WeMessageHandle(web.View):
    """
    企业微信发送信息类
    """
    async def post(self):
        wmm = WeMessageModule()
        # 获取Post body体内容
        req_data: dict = await self.request.json()
        wmm.from_app: str = req_data["from"] if req_data.get("from") else None
        # to 标识发送到 chat_group
        wmm.to_chat: str = req_data["to"] if req_data.get("to") else None
        # user 单独发送到用户, 需要自己拼写微信ID, 格式: "ID1|ID2|ID3"
        wmm.to_user: str = req_data["user"] if req_data.get('user') else None
        wmm.content: str = req_data["content"] if req_data.get("content") else None
        if wmm.to_chat is None and wmm.to_user is None or wmm.from_app is None or wmm.content is None:
            return web.Response(text="Error: POST body 'from, content, (to/user)' is required")

        result = await MessageService().send_message(wmm)
        return web.Response(text=result)


class WeGroupHandle(web.View):
    """
    企业微信组管理类
    """

    async def get(self):
        ret = await ChatGroup().create_admin_group()
        return web.Response(text=ret)

    async def post(self):
        # 获取Post body体内容
        try:
            req_data: dict = await self.request.json()
        except json.decoder.JSONDecodeError:
            # 处理POST请求体为空的情况
            req_data = {}

        group_name: str = req_data.get("name")
        users: str = req_data.get("users")
        if users is not None:
            # 如果users不为空, 将其转为列表
            users: list = users.split(",")

        result = await ChatGroup().create_group_chat(group_name, users)

        return web.Response(text=result)

