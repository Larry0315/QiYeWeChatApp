
class ResponseError(Exception):
    """
    响应异常
    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class PathError(Exception):
    """
    Path 路径异常
    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class RequestError(Exception):
    """
    请求异常
    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class PickUpDataError(Exception):
    """
    解析 Zabbix 报警内容异常
    """

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message
