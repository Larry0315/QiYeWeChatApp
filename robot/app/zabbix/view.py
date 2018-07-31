from typing import List
from utils.logger_helper import LogFactory
from utils.error_helper import PickUpDataError
from app.zabbix.service import ZabbixService

logger = LogFactory.get_logger()


class ZabbixHandle:
    """
    Zabbix 服务接口的接口层
    """

    @classmethod
    def pick_up_data(cls, content: str) -> dict:
        """
        提取Zabbix报警内容中的信息 (信息: 以这些信息为依据取得image)
        :param: content
        :return: dict
        """
        logger.info("原始内容: {0}".format(content))
        # 初始化数据字典
        content_data: dict = {"hostname": "", "alert_item": "", "event_id": ""}
        content: List[str] = content.split("\n")
        for i in content:
            if i.strip().startswith("告警主机"):
                hostname: str = i.split("：")[1].replace("\r", "")
                content_data["hostname"] = hostname
                logger.info(u'告警主机/hostname: {0}'.format(hostname))
                # hostname = hostname.encode(encoding='utf-8')
            elif i.strip().startswith("告警项目"):
                alert_item = i.split("：")[1].replace("\r", "")
                content_data["alert_item"] = alert_item
                logger.info("告警项目/alert_item: {0}".format(alert_item))
            elif i.strip().startswith("事件ID"):
                event_id = i.split("：")[1].replace("\r", "")
                content_data["event_id"] = event_id
                logger.info("事件ID/event_id: {0}".format(event_id))
            else:
                continue
        # 如果其中任意一项无法提取, 即抛出异常
        if content_data.get("hostname") or content_data.get("alert_item") or content_data.get("event_id"):
            return content_data
        else:
            err_info = "解析Zabbix报警信息失败 hostname: {0}, alert_item: {1}, eventid: {2}"\
                .format(content_data["hostname"], content_data["alert_item"], content_data["eventid"])
            logger.error(err_info)
            raise PickUpDataError(err_info)

    @classmethod
    async def get_image_path(cls, content: str) -> str:
        """
        根据传递的content内容信息, 下载对应的image并返回下载完成后的Image路径
        :param content: zabbix 故障报警信息原始内容
        :return: Image path路径
        """
        content_data: dict = cls.pick_up_data(content)
        zs = ZabbixService()
        hostname: str = content_data.get("hostname")
        trigger: str = content_data.get("alert_item")
        event_id: str = content_data.get("event_id")
        image_path: str = await zs.get_image_path(hostname=hostname, trigger=trigger, event_id=event_id)
        return image_path

