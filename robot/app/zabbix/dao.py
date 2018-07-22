import os
import time
import aiohttp
import aiofiles
from utils.logger_helper import slog
from utils.session_helper import Session
from aiohttp.client_reqrep import ClientResponse
from utils.db_helper import MySQLConnector
from aiomysql.pool import Pool
from aiomysql.connection import Connection
from aiomysql.cursors import Cursor
from config.robot_cfg import image_path
from http.cookies import SimpleCookie
from config.robot_cfg import zbx_user, zbx_password, \
    zbx_login_url, zbx_download_url


class ZabbixDao:
    """
    Zabbix 数据访问类, 支持获取 Zabbix Cookies,
    查询 Zabbix 数据库信息, 下载趋势图表
    """
    def __init__(self):
        self.username: str = zbx_user
        self.password: str = zbx_password
        self.cookies: SimpleCookie = None
        self.expires: int = 0
        self.interval: int = 60 * 60 * 24 * 20
        self.login_url: str = zbx_login_url
        self.download_url: str = zbx_download_url

    async def get_cookie(self) -> SimpleCookie:
        """
        登录 Zabbix 获取 cookies(SimpleCookie)
        :return:
        """
        # 设置登录的信息
        login_data: dict = {
            "name": self.username,
            "password": self.password,
            "autologin": 1,
            "enter": "Sign in"
        }

        # 登录zabbix系统
        session: aiohttp.client.ClientSession = Session.get_session()

        resp: ClientResponse
        async with session.post(self.login_url, data=login_data) as resp:
            # 获取cookies(SimpleCookie对象)
            self.cookies: SimpleCookie = resp.cookies

        # 设置cookies过期时间为当前时间戳+20天
        self.expires = int(time.time()) + self.interval

        slog.info("获取新的 Zabbix Cookies, 过期时间戳: {0}".format(self.expires))
        return self.cookies

    @staticmethod
    async def get_host_id(hostname: str) -> int:
        """
        根据主机名, 查询对应的主机id
        :param hostname:
        :return:
        """
        sql: str = "select hostid from hosts where name='{0}';".format(hostname)
        slog.info("查询主机ID SQL: {0}".format(sql))
        # 获取连接池对象
        pool: Pool = await MySQLConnector.get_conn()
        assert pool, "连接池对象为空, 请检查该服务到MySQL的连接配置属性"
        # 获取 MySQL 连接
        conn: Connection
        async with pool.acquire() as conn:
            # 获取游标
            cur: Cursor
            async with conn.cursor() as cur:
                # 执行 SQL 语句
                await cur.execute(sql)
                slog.info(cur.description)
                # 获取结果(精确查找, 只返回一条记录)
                (result,) = await cur.fetchone()
                host_id: int = int(result)
                slog.info("查询主机ID结果: {0}".format(host_id))
                return host_id

    @staticmethod
    async def get_item_id(host_id: int, trigger_name: str) -> int:
        """
        根据主机id和触发器名称获取项目id
        :param host_id: 主机id
        :param trigger_name: 触发器名称
        :return: 项目id
        """
        # 处理触发器字符串
        trigger_name: str = trigger_name.replace("'", "\\'")
        slog.info("trigger_name/key: {0}".format(trigger_name))
        sql: str = "select itemid from items where hostid={0} and key_='{1}';".format(host_id, trigger_name)
        slog.info("查询项目ID SQL: {0}".format(sql))
        # 获取连接池对象
        pool: Pool = await MySQLConnector.get_conn()
        assert pool, "连接池对象为空, 请检查该服务到MySQL的连接配置属性"
        # 获取 MySQL 连接
        conn: Connection
        async with pool.acquire() as conn:
            # 获取游标
            cur: Cursor
            async with conn.cursor() as cur:
                # 执行 SQL 语句
                await cur.execute(sql)
                slog.info(cur.description)
                # 获取结果(精确查找, 只返回一条记录)
                (result,) = await cur.fetchone()
                item_id: int = int(result)
                slog.info("查询项目ID结果: {0}".format(item_id))
                return item_id

    async def from_hostname_to_itemid(self, hostname: str, trigger_name: str) -> int:
        """
        根据主机名和触发器名称, 查询项目id
        :param hostname: 主机名
        :param trigger_name: 触发器名称
        :return: 项目id
        """
        host_id: int = await self.get_host_id(hostname)
        item_id: int = await self.get_item_id(host_id, trigger_name)
        return item_id

    async def download_iamge(self, item_id: int, event_id: str=None) -> str:
        """
        下载最近一小时的趋势图
        :return: 保存的文件路径
        """
        # 设置下载图表接口地址
        download_url: str = "{0}?itemids={1}&period=3600".format(self.download_url, str(item_id))
        slog.info("监控趋势图下载地址: {0}".format(download_url))

        # 创建/检查图表路径
        try:
            if not os.path.isdir(image_path):
                os.mkdir(image_path)
        except Exception as e:
            slog.error("创建保存图片的文件夹失败, 路径: {0} \n{1}".format(image_path, e))

        # 设置图片保存路径
        if not event_id:
            event_id = time.time()
        full_path = "{0}/{1}-{2}.png".format(image_path, item_id, event_id)
        slog.info("保存图片完整路径: {0}".format(full_path))

        # 验证cookies是否可用
        if self.cookies is None or self.expires <= int(time.time()):
            slog.info("获取新的cookies")
            # 先将 Zabbix Session 对象置空
            Session.zabbix_session_instance = None
            # 再获取新的 SimpleCookie 对象
            await self.get_cookie()

        # 获取带 cookie 的 session 对象
        session = Session.get_zabbix_session(self.cookies)

        resp: ClientResponse
        async with session.get(download_url) as resp:
            async with aiofiles.open(full_path, mode='wb') as f:
                # 将 Response Body 以二进制方式读取, 写入文件(一次性读取)
                await f.write(await resp.read())
                slog.info("图片已下载至 {0}".format(full_path))

        # 返回图片所在的绝对路径
        return full_path

