import asyncio
import uvloop
import logging
from aiohttp import web
from routes import setup_routes
from config import robot_cfg as cfg
from utils.session_helper import Session
from utils.db_helper import MySQLConnector
from utils.logger_helper import slog


async def shutdown(app):
    print("Shutting Down The Server...")

    print("Close Session...")
    await Session.close_all_session()
    print("Close Session, Done")

    print("Close MySQL Connect Pool...")
    await MySQLConnector.close_conn()
    print("Close MySQL Connect Pool, Done")


def main():
    logging.basicConfig(filename='logs/robot.log', level=logging.DEBUG)
    slog.info("Server Starting at {0};{1}".format(cfg.host, cfg.port))
    app = web.Application()
    setup_routes(app)
    app.on_shutdown.append(shutdown)
    web.run_app(app, host=cfg.host, port=cfg.port)


if __name__ == "__main__":
    # 使用 uvloop 替换掉 asyncio 默认的事件循环
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # 启动 Server
    try:
        main()
    except Exception as e:
        slog.error(e)
