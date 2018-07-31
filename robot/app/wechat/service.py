import time
import ujson
import xml.etree.cElementTree as Et
# from utils.logger_helper import slog
from utils.xml_helper import CDATA
from utils.wechat_helper import WeCrypt, random_str6
from utils.error_helper import ResponseError
from config.robot_cfg import corpname, corpid, \
    app_name, agentid, corpsecret, token_url, chat_group_create, \
    contact, msg_chatgroup_url, msg_url, upload_res_url, \
    paas_chat_id, get_user_info_url, super_user, default_group_user
from app.wechat import dao
from app.wechat.module import WeMessageModule
from app.zabbix.view import ZabbixHandle
from utils.logger_helper import LogFactory

logger = LogFactory.get_logger()


class WeChat:
    """
    微信类
    """
    def __init__(self):
        self.corpname: str = corpname
        self.corpid: str = corpid


class PaaSAPP(WeChat):
    """
    PaaS应用
    """
    token: str = ""
    token_expiration_time: int = 0
    offset: int = 60

    def __init__(self):
        super(PaaSAPP, self).__init__()
        self.app_name: str = app_name
        self.agentid: str = agentid
        self.corpsecret: str = corpsecret
        # self.token: str = ""
        # token_expiration_time = time.time() + expires_in - offset
        # self.token_expiration_time: int = 0
        # 声明在微信Token过期前x秒进行本地过期, 重新获取新的Token
        # self.offset: int = 60

    async def get_token_from_official(self) -> bool:
        """
        从微信接口中获取Token
        :return: dict token and expires
        """
        # 构建请求参数
        param = {'corpid': self.corpid, 'corpsecret': self.corpsecret}
        logger.info("corpid: {0}, corpsecret: {1}".format(self.corpid, self.corpsecret))
        # 发起 http 请求
        ret: str = await dao.get(url=token_url, params=param)
        # 获取响应体内容
        logger.info(u"获取Token: {0}".format(ret))
        rep_body: dict = ujson.loads(ret)
        logger.info(rep_body)

        try:
            if rep_body['errcode'] == 0:
                # 获取接口返回的Token过期时间, 在对象中过期时间(时间戳)
                PaaSAPP.token: str = rep_body['access_token']
                # 在微信服务器Token过期前进行本地过期
                PaaSAPP.token_expiration_time: int = time.time() + rep_body['expires_in'] - PaaSAPP.offset
                return True
        except ResponseError as e:
            logger.info(u"获取企业微信Token失败 {0}".format(e))
            logger.info(u"微信返回错误信息: {0}".format(ret))
            return False

    async def get_token(self) -> str:
        """
        获取可用的Token, 当内存中的Token不可用时, 获取新的Token
        :return:
        """
        if PaaSAPP.token == "" or PaaSAPP.token_expiration_time == 0 or PaaSAPP.token_expiration_time <= time.time():
            logger.info(u"Token不可用或即将过期, 重新获取Token")
            token: bool = await self.get_token_from_official()
            if token:
                logger.info(u"Token获取成功: {0}".format(PaaSAPP.token))
                return PaaSAPP.token
            else:
                logger.info(u"Token获取失败")
        else:
            logger.info(u"Token未过期, 复用Token {0}".format(PaaSAPP.token))
            return PaaSAPP.token

    async def send(self, message: dict, url: str) -> str:
        message: str = ujson.dumps(message, ensure_ascii=False).encode('utf8')
        logger.info(u"待发送的消息: {0}".format(message))

        # 获取token
        token: str = await self.get_token()
        result_body: str = await dao.post(url=url, params={'access_token': token}, data=message)
        logger.info(u"发送消息状态: {0}".format(result_body))
        return result_body

    async def upload_image(self, image_path) -> str:
        """
        上传临时素材, 过期时间为上传日期+3天
        :param image_path: 上传文件路径
        :return: image_id
        """
        # 获取token
        token: str = await self.get_token()
        params = {'access_token': token, "type": "image"}
        result: str = await dao.post_file(url=upload_res_url, file_path=image_path, params=params)
        result_body: dict = ujson.loads(result)
        logger.info(u"上传后取得的资源ID: {0}".format(result_body['media_id']))
        return result_body['media_id']


class MessageService(PaaSAPP):
    """
    企业微信发送信息-业务逻辑层
    """

    message_instance = None

    @classmethod
    def get_message_obj(cls):
        if cls.message_instance:
            return cls.message_instance
        else:
            cls.message_instance = MessageService()
            return cls.message_instance

    async def send_message_to_user(self, users: str, content: str):
        message: dict = {
            "msgtype": "text",
            "safe": 0,
            "agentid": self.agentid,
            "touser": users,
            "text": {"content": content}
        }
        logger.info("to_user: {0}, content: {1}".format(users, content))
        return await self.send(message, msg_url)

    async def send_message_to_chat_group(self, chat_id: str, content: str) -> str:
        message: dict = {
            "chatid": chat_id,
            "msgtype": "text",
            "text": {"content": content},
            "safe": 0
        }
        logger.info("to_chat: {0}, content: {1}".format(chat_id, content))
        return await self.send(message, msg_chatgroup_url)

    async def send_image_to_user(self, users: str, image_id: str):
        message: dict = {
            "msgtype": "image",
            "safe": 0,
            "agentid": self.agentid,
            "touser": users,
            "image": {"media_id": image_id}
        }
        logger.info("to_user: {0}, image_id: {1}".format(users, image_id))
        return await self.send(message, msg_url)

    async def send_image_to_chat_group(self, chat_id: str, image_id: str):
        message: dict = {
            "msgtype": "image",
            "safe": 0,
            "chatid": chat_id,
            "image": {"media_id": image_id}
        }
        logger.info("to_chat: {0}, image_id: {1}".format(chat_id, image_id))
        return await self.send(message, msg_chatgroup_url)

    async def send_message(self, wmm: WeMessageModule):

        if wmm.to_user:
            await self.send_message_to_user(users=wmm.to_user, content=wmm.content)
        else:
            await self.send_message_to_chat_group(chat_id=wmm.to_chat, content=wmm.content)

        # 对Zabbix报警做特殊处理
        if wmm.from_app.strip().lower() == "zabbix" and wmm.content.strip().startswith("PROBLEM"):
            logger.info("收到Zabbix Problem报警信息, 获取一小时趋势图")
            # 获取故障报警最近一小时的趋势图
            zh: ZabbixHandle = ZabbixHandle()
            # 根据报警内容下载趋势图, 取得下载后的图片的绝对路径
            image_path: str = await zh.get_image_path(content=wmm.content)
            logger.info("图片已下载至: {0}".format(image_path))
            # 上传图像至微信
            image_id: str = await self.upload_image(image_path=image_path)

            if wmm.to_user:
                await self.send_image_to_user(users=wmm.to_user, image_id=image_id)
            else:
                await self.send_image_to_chat_group(chat_id=wmm.to_chat, image_id=image_id)

        # # 对Zabbix报警做特殊处理
        # if wmm.from_app.strip().lower() == "zabbix" and wmm.content.strip().startswith("PROBLEM"):
        #     # 获取故障报警最近一小时的趋势图
        #     zh: ZabbixHandle = ZabbixHandle()
        #     # 根据报警内容下载趋势图, 取得下载后的图片的绝对路径
        #     image_path: str = await zh.get_image_path(content=wmm.content)
        #     # 上传图像至微信
        #     image_id: str = await self.upload_image(image_path=image_path)
        #
        #     if wmm.to_user:
        #         await self.send_message_to_user(users=wmm.to_user, content=wmm.content)
        #         await self.send_image_to_user(users=wmm.to_user, image_id=image_id)
        #     else:
        #         await self.send_message_to_chat_group(chat_id=wmm.to_chat, content=wmm.content)
        #         await self.send_image_to_chat_group(chat_id=wmm.to_chat, image_id=image_id)
        # else:
        #     if wmm.to_user:
        #         await self.send_message_to_user(users=wmm.to_user, content=wmm.content)
        #     else:
        #         await self.send_message_to_chat_group(chat_id=wmm.to_chat, content=wmm.content)


class WeChatService(WeChat):
    """
    企业微信信息交互-业务逻辑层
    """
    def __init__(self):
        super(WeChatService, self).__init__()
        # 获取企业微信加密/解密对象
        self.we_crypt = WeCrypt.get_we_crype()

    def echo(self, msg_sig, timestamp, nonce, echo) -> str:
        """
        用于解密建立连接的验证加密串
        :param msg_sig:
        :param timestamp:
        :param nonce:
        :param echo: 加密字符串
        :return:
        """
        # 进行URL认证
        ret: tuple = self.we_crypt.VerifyURL(msg_sig, timestamp, nonce, echo)
        ret_code: int = ret[0]
        echo_str: bytes = ret[1]
        if ret_code != 0:
            # raise error
            return "ERR: VerifyURL ret: {0}".format(ret)
        return echo_str.decode(encoding='utf-8')

    def decode_body(self, req_data, msg_sig, timestamp, nonce) -> bytes:
        """
        解密消息体
        :param req_data: 加密消息体
        :param msg_sig:
        :param timestamp:
        :param nonce:
        :return:
        """
        # 进行URL认证, 将企业微信发送过来的加密串进行解密
        ret = self.we_crypt.DecryptMsg(req_data, msg_sig, timestamp, nonce)
        ret_code: int = ret[0]
        msg: bytes = ret[1]
        if ret_code != 0:
            raise Exception
            # return "ERR: DecryptMsg ret: {0}".format(ret)
        return msg

    @staticmethod
    async def rep_body(msg) -> str:
        """
        根据用户发来的消息进行回复, 一期为echo server; 二期将做区分命令和普通消息的处理
        :param msg: 明文消息体xml
        :return: 明文消息体xml
        """
        # 根据接收到的xml消息，实例化成xml对象
        xml_tree = Et.fromstring(msg)

        # 只处理发送消息的事件
        # if xml.etree.ElementTree.iselement(xml_tree.find("Content")):
        if Et.iselement(xml_tree.find("Content")):
            # 获取用户发送的消息
            content: str = xml_tree.find("Content").text
        else:
            # raise error
            logger.info("Only Support Message Event")
            return "Only Support Message Event"

        user_id: str = xml_tree.find("FromUserName").text  # 用户id
        corp_id: str = xml_tree.find("ToUserName").text  # 企业id
        create_time: str = xml_tree.find("CreateTime").text  # 时间戳（用request的时间戳即可

        # 构建xml树
        rep_data: Et.Element = Et.Element("xml")
        to_user_name: Et.Element = Et.SubElement(rep_data, "ToUserName")
        from_user_name: Et.Element = Et.SubElement(rep_data, "FromUserName")
        rep_create_time: Et.Element = Et.SubElement(rep_data, "CreateTime")
        message_type: Et.Element = Et.SubElement(rep_data, "MsgType")
        rep_content: Et.Element = Et.SubElement(rep_data, "Content")

        # 创建CDATA对象
        to_user_name_cdata = CDATA(user_id)
        from_user_name_cdata = CDATA(corp_id)
        message_type_cdata = CDATA("text")
        rep_content_cdata = CDATA("📮 消息已转发至PaaS团队🍪")

        # 插曲~ 将用户发来的信息, 转发到 paas chat group
        user_info: dict = await WeUser().get_user_info(user_id=user_id)
        transmit_content = "📨 From: {0} {1} \n📒 Details: {2}".format(user_info["name"], user_info["position"], content)
        message_obj: MessageService = MessageService.get_message_obj()
        await message_obj.send_message_to_chat_group(paas_chat_id, transmit_content)

        # 为节点赋值
        to_user_name.append(to_user_name_cdata)
        from_user_name.append(from_user_name_cdata)
        rep_create_time.text = create_time
        message_type.append(message_type_cdata)
        rep_content.append(rep_content_cdata)

        # 生成明文的xml回文
        rep_xml_data: str = Et.tostring(rep_data, encoding="utf-8", method="xml").decode(encoding='utf-8')
        return rep_xml_data

    def encode_body(self, rep_xml_data, nonce, timestamp) -> str:
        """
        加密消息体
        :param rep_xml_data: 明文消息体
        :param nonce:
        :param timestamp:
        :return: 密文消息体
        """
        ret: tuple = self.we_crypt.EncryptMsg(rep_xml_data, nonce, timestamp)
        ret_code: int = ret[0]
        encrypt_msg: str = ret[1]
        if ret_code != 0:
            # raise error
            return "ERR: EncryptMsg ret: {0}".format(ret)
        return encrypt_msg

    def __administrator_cmd(self):
        """
        处理 => 管理员命令
        :return:
        """
        pass

    def __user_cmd(self):
        """
        处理 -> 用户命令
        :return:
        """
        pass

    def __user_msg(self):
        """
        处理用户普通消息
        :return:
        """
        pass


class ChatGroup(PaaSAPP):
    """
    企业微信聊天组管理
    """
    async def create_admin_group(self):

        userlist: list = list(contact.values())
        message: dict = {
            "name": "😈PaaS团队😈",
            "owner": "039273",
            "userlist": userlist
        }
        message: str = ujson.dumps(message, ensure_ascii=False).encode('utf8')

        # 获取token
        token: str = await self.get_token()

        params = {'access_token': token}
        ret: str = await dao.post(url="https://qyapi.weixin.qq.com/cgi-bin/appchat/create", data=message, params=params)
        logger.info(ret)
        return ret

    async def create_group_chat(self, chat_name: str=None, userlist: list=None):
        # 如果用户为None, 按默认用户生成组
        if userlist is None:
            userlist: list = default_group_user
        elif super_user not in userlist:
            # 如果用户列表里不包含管理员, 强制添加管理员
            userlist.append(super_user)
        # 如果组名为空, 设置为随机6位字符串
        if chat_name is None:
            chat_name: str = random_str6()

        # 构建消息体
        message: dict = {
            "name": chat_name,
            "owner": super_user,
            "userlist": userlist
        }
        message: str = ujson.dumps(message, ensure_ascii=False).encode('utf8')

        # 获取token
        token: str = await self.get_token()

        params = {'access_token': token}
        ret: str = await dao.post(url=chat_group_create, data=message, params=params)
        return ret


class WeUser(PaaSAPP):
    """
    企业微信用户信息查询
    """



    async def get_user_info(self, user_id: str):
        # 获取token
        token: str = await self.get_token()
        # 构建请求参数
        param = {'access_token': token, 'userid': user_id}
        # 发起 http 请求
        ret: str = await dao.get(url=get_user_info_url, params=param)
        # 获取响应体内容
        rep_body: dict = ujson.loads(ret)
        logger.info(rep_body["name"], rep_body["position"])
        return rep_body
