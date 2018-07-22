
class WeMessageModule:
    """
    微信消息实体层
    """

    def __init__(self):
        self.from_app: str = None
        self.to_chat: str = None
        self.to_user: str = None
        self.content: str = None
