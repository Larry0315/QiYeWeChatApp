import uuid
import random
from config import robot_cfg
from utils.WXBizMsgCrypt import WXBizMsgCrypt as we_crypt


class WeCrypt:
    """
    企业微信加密/解密类
    """

    we_crypt_instance: we_crypt = None
    token: str = robot_cfg.we_token
    aes_key: str = robot_cfg.we_encoding_AESKey
    corp_id: str = robot_cfg.corpid

    @classmethod
    def get_we_crype(cls) -> we_crypt:
        """
        单例模式
        获取企业微信加密/解密对象
        :return:
        """
        if cls.we_crypt_instance:
            return cls.we_crypt_instance
        else:
            cls.we_crypt_instance = we_crypt(cls.token, cls.aes_key, cls.corp_id)
            return cls.we_crypt_instance


def random_str6() -> str:
    """
    获取一个6位的随机字符串
    生成规则: 生成uuid --> 去掉uuid中的"-" --> 使用random随机挑选6个字符
    :return: str
    """
    return "".join(random.sample(str(uuid.uuid1()).replace("-", ""), 6))
