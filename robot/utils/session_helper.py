import aiohttp
import ujson
from http.cookies import SimpleCookie
from utils.logger_helper import LogFactory

logger = LogFactory.get_logger()


class Session:
    """
    获取 http client session
    单例模式, 全局复用 session
    """
    session_instance: aiohttp.client.ClientSession = None
    zabbix_session_instance: aiohttp.client.ClientSession = None

    @classmethod
    def get_session(cls):
        """
        获取 aiohttp client session 对象
        已创建过对象直接返回, 反之, 先创建再返回
        :return:
        """
        if cls.session_instance:
            logger.info("Session 复用 {0}".format(cls.session_instance))
            return cls.session_instance
        else:
            cls.session_instance = aiohttp.ClientSession(json_serialize=ujson.dumps)
            logger.info("新 Session 对象已被创建 {0}".format(cls.session_instance))
            return cls.session_instance

    @classmethod
    def get_zabbix_session(cls, cookies: SimpleCookie):
        """
        使用自定义 cookies 的 session 对象
        单例模式, 需要自己判断 cookie 是否过期, 如果过期
        需要先 Session.cookie_session_instance=None, 再获取 session
        WARNING: 本例中 Cookie 复用的唯一场景为: Zabbix cookies 复用
        :param cookies: 接收 SimpleCookie 对象
        :return:
        """
        if cls.zabbix_session_instance:
            logger.info("Zabbix Session 复用 {0}".format(cls.zabbix_session_instance))
            return cls.zabbix_session_instance
        else:
            jar = aiohttp.CookieJar(unsafe=True)
            jar.update_cookies(cookies)
            cls.zabbix_session_instance = aiohttp.ClientSession(cookie_jar=jar,
                                                                json_serialize=ujson.dumps)
            logger.info("新 Zabbix Session 对象已被创建 {0}".format(cls.zabbix_session_instance))
            return cls.zabbix_session_instance

    @classmethod
    async def close_session(cls):
        """
        关闭 Session 对象
        :return:
        """
        if cls.session_instance:
            await cls.session_instance.close()
            logger.info("Session 连接对象已被关闭")

    @classmethod
    async def close_zabbix_session(cls):
        """
        关闭 Zabbix 专用的 Session 对象
        :return:
        """
        if cls.zabbix_session_instance:
            await cls.zabbix_session_instance.close()
            logger.info("Zabbix Session 连接对象已被关闭")

    @classmethod
    async def close_all_session(cls):
        """
        关闭所有 Session 对象
        :return:
        """
        await cls.close_session()
        await cls.close_zabbix_session()
