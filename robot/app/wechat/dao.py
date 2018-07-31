import os
from utils.session_helper import Session
from aiohttp.client_reqrep import ClientResponse
from utils.error_helper import PathError, ResponseError
from utils.logger_helper import LogFactory
from aiohttp import FormData

logger = LogFactory.get_logger()


async def get(url: str, params: dict) -> str:
    """
    GET 方式获取URL地址内容
    :param url: http(s)://url
    :param params: params
    :return: ClientResponse
    """
    # 获取 aiohttp client session 对象
    session = Session.get_session()
    # 访问URL, 返回 ClientResponse 结果对象
    resp: ClientResponse
    async with session.get(url, params=params) as resp:
        logger.info("GET {0}, status: {1}".format(resp.url, resp.status))
        if resp.status not in (200, 201):
            raise ResponseError("{0} Response Error {1}".format(resp.url, resp.status))
        return await resp.text()


async def post(url: str, params: dict=None, data: str=None) -> str:
    """
    POST 方式获取URL地址内容
    :param url: http(s)://url
    :param params:  params
    :param data: post body str/None
    :return: ClientResponse
    """
    # 获取 aiohttp client session 对象
    session = Session.get_session()
    # 访问URL, 返回 ClientResponse 结果对象
    resp: ClientResponse
    async with session.post(url, data=data, params=params) as resp:
        logger.info("POST {0}, status: {1}".format(resp.url, resp.status))
        return await resp.text()


async def post_file(url: str, file_path: str, params: dict=None) -> ClientResponse:
    """
    POST 方式上传文件
    :param url:
    :param file_path: 文件路径
    :param params:
    :return:
    """
    if not os.path.exists(file_path):
        logger.info("image_path: {0} 上传路径不存在".format(file_path))
        raise PathError("image_path: {0} 上传路径不存在".format(file_path))
    image_name = file_path.split("/")[-1]
    logger.info("image_name: {0}".format(image_name))
    # 获取 aiohttp client session 对象
    session = Session.get_session()
    with open(file_path, "rb") as f:
        logger.info("{0} 文件准备上传".format(file_path))
        data = FormData()
        data.add_field('media', f, content_type="multipart/form-data",
                       filename=image_name)
        resp: ClientResponse
        async with session.post(url, data=data, params=params) as resp:
            logger.info("POST {0}, status: {1}".format(resp.url, resp.status))
            return await resp.text()
