from app.zabbix.dao import ZabbixDao


class ZabbixService:
    """
    Zabbix 接口的业务逻辑层
    """

    @staticmethod
    async def get_image_path(hostname: str, trigger: str, event_id: str) -> str:
        """
        根据报警信息, 下载最近一小时的趋势图到本地, 并返回保存的本地路径
        :return:
        """
        # 根据hostname和trigger得到item_id
        zd = ZabbixDao()
        item_id: int = await zd.from_hostname_to_itemid(hostname=hostname, trigger_name=trigger)

        # 下载图像
        image_path: str = await zd.download_iamge(item_id, event_id)

        return image_path

