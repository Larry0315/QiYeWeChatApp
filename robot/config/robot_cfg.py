# 本配置为示例配置
# listen
host = "0.0.0.0"
port = 8080

# wechat-receive-config 
we_token = "yyyyyyyyyyy"
we_encoding_AESKey = "oooooooooooooooooooo"

# wechat-config
corpname = "name"
corpid = "uuuuuuuuuuuuuuuuu"
app_name = "paas"
agentid = 1000001
corpsecret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# wechat-url
wechat_base_url = "https://qyapi.weixin.qq.com/cgi-bin"
token_url: str = "{0}/gettoken".format(wechat_base_url)
msg_url: str = "{0}/message/send".format(wechat_base_url)
msg_chatgroup_url: str = "{0}/appchat/send".format(wechat_base_url)
upload_res_url: str = "{0}/media/upload".format(wechat_base_url)
get_res_url: str = "{0}/media/get".format(wechat_base_url)
chat_group_create: str = "{0}/appchat/create".format(wechat_base_url)
chat_group_update: str = "{0}/appchat/update".format(wechat_base_url)
chat_group_get: str = "{0}/appchat/get".format(wechat_base_url)
get_user_info_url: str = "{0}/user/get".format(wechat_base_url)

# paas特权列表
super_user = "userid"
default_group_user: list = ["userid", "userid2"]

contact: dict = {
    "admin": "userid",
}

# paas group chat
paas_chat_id: str = "kkkkkkkkkkkkkkkkkk"

# MySQL
my_user: str = "zabbix"
my_pwd: str = "password"
my_host: str = "10.10.10.10"
my_port: int = 3306
my_db: str = "zabbix"
my_minsize: int = 10
my_maxsize: int = 20
my_charset: str = "utf8"

# 图片保存路径(最后不需要有/)
image_path: str = "/tmp/zabbix_graph"

zbx_user = "admin"
zbx_password = "zabbix"
zbx_login_url = "http://m.lvrui.io/index.php"
zbx_download_url = "http://m.lvrui.io/chart.php"


