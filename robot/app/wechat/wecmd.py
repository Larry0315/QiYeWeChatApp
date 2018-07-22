from config.robot_cfg import contact


def fp_cmd(message: str, user_id: str):
    """
    判断字符串是否为命令
    :param message:
    :param user_id:
    :return:
    """
    # 匹配命令关键字符 "=> " 且 输入该命令的用户为管理员用户
    if message.strip().startswith("=> ") and user_id in contact.values():
        # message 为命令
        pass
    else:
        # 普通消息, 直接返回
        return message






############ 管理员操作

# => 操作类型[GET/POST/PUT/DELETE] 操作资源[wechat.group] 操作对象[admin]

# 增加组
# => POST wechat.group 组名 a.finupgroup.com b.finupgroup.com c.finupgroup.com

# 查询组员
# => GET wechat.group 组名


########### 用户操作

# 增加组[添加到待审核清单]
# -> POST wechat.group 组名 a.finupgroup.com b.finupgroup.com c.finupgroup.com

# 删除组员[添加到待审核清单]
# -> DELETE wechat.group 组名 c.finupgroup.com

# 变更成员[添加到待审核清单]
# -> PUT wechat.group 组名 b.finupgroup.com d.finupgroup.com

# 查询组员
# -> GET wechat.group 组名

# 查询所有组
# -> GET wechat.group

# 查询所有组以及组下成员
# -> GET wechat.group --all

# 微信组操作帮助
# -> GET wechat.group.help

# 微信操作帮助
# -> GET wechat.help

# 所有可以操作的对象
# -> GET help
