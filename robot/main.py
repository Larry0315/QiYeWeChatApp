import asyncio
import uvloop
from aiohttp import web
from routes import setup_routes
from config import robot_cfg as cfg
from utils.session_helper import Session
from utils.db_helper import MySQLConnector
from utils.logger_helper import LogFactory

logger = LogFactory.get_logger()


async def shutdown(app):
    logger.info("Shutting Down The Server...")

    logger.info("Close Session...")
    await Session.close_all_session()
    logger.info("Close Session, Done")

    logger.info("Close MySQL Connect Pool...")
    await MySQLConnector.close_conn()
    logger.info("Close MySQL Connect Pool, Done")


def main():
    logger.info("Server Starting at {0};{1}".format(cfg.host, cfg.port))
    app = web.Application()
    setup_routes(app)
    app.on_shutdown.append(shutdown)
    web.run_app(app, host=cfg.host, port=cfg.port)


# For Gunicorn
async def web_app():
    # 使用 uvloop 替换掉 asyncio 默认的事件循环
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    logger.info("Server Starting at {0};{1}".format(cfg.host, cfg.port))
    app = web.Application()
    setup_routes(app)
    app.on_shutdown.append(shutdown)
    return app


if __name__ == "__main__":
    # 使用 uvloop 替换掉 asyncio 默认的事件循环
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # 启动 Server
    try:
        main()
    except Exception as e:
        logger.error(e)
