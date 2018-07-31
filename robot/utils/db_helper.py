from aiomysql.pool import Pool
from aiomysql import create_pool
from utils.logger_helper import LogFactory
from logging import Logger
from config.robot_cfg import my_host, my_port, \
    my_db, my_user, my_pwd, my_minsize, my_maxsize, my_charset

logger: Logger = LogFactory.get_logger()


class MySQLConnector:
    """
    在连接池里获取MySQL连接对象, MySQL连接池的创建为单例模式, 复用一个连接池
    连接池用法:
        获取连接池对象
        获取一个连接
        基于连接创建游标
        使用游标执行SQL
        获取SQL执行结果
        关闭游标
    """
    connector: Pool = None

    @classmethod
    async def get_conn(cls):
        """
        获取连接池对象, 如果创建连接池异常, 返回的对象值为空
        :return:
        """
        if cls.connector:
            logger.info("MySQL连接池对象复用")
            return cls.connector
        else:
            try:
                logger.info("创建MySQL连接池对象")
                # 创建连接池对象
                cls.connector: Pool = await create_pool(host=my_host, port=my_port,
                                                        user=my_user, password=my_pwd,
                                                        db=my_db, charset=my_charset,
                                                        minsize=my_minsize, maxsize=my_maxsize)
                logger.info("MySQL数据库连接池已创建\n{0}".format(type(cls.connector)))
            except Exception as ex:
                logger.info("MySQL数据库连接池创建异常\n{0}".format(ex))
            finally:
                return cls.connector

    @classmethod
    def __del_conn(cls):
        cls.connector: Pool = None
        logger.info("清除连接池对象\n".format(type(cls.connector)))

    @classmethod
    async def close_conn(cls):
        """
        关闭连接池
        步骤:
            将类连接池对象置空
            关闭连接池
        :return:
        """
        if cls.connector:
            # 关闭连接池
            cls.connector.close()
            logger.info("正在关闭MySQL连接池")
            # 等待连接处理完毕
            await cls.connector.wait_closed()
            logger.info("MySQL连接池已关闭")
        # 为单例模式清空连接池对象的值
        cls.__del_conn()
