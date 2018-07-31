import os
import logging
import logging.config
import logging.handlers
from config.robot_cfg import service_name, log_path

SERVICE_NAME = service_name
LOG_PATH = log_path

if not os.path.isdir(log_path):
    os.mkdir(log_path)


class InfoFilter(logging.Filter):
    def filter(self, record):
        """
        只筛选出INFO级别的日志
        """
        if logging.INFO <= record.levelno < logging.ERROR:
            return super().filter(record)
        else:
            return 0


class ErrorFilter(logging.Filter):
    def filter(self, record):
        """
        只筛选出ERROR级别的日志
        """
        if logging.ERROR <= record.levelno < logging.CRITICAL:
            return super().filter(record)
        else:
            return 0


class LogFactory:

    # 单例日志对象
    logger_instance: dict = {}

    # 日志切割方式按天
    LOG_SPLIT_TYPE = "d"
    # 切割周期每天
    LOG_SPLIT_INTERVAL = 1
    # 保存日志数量
    LOG_BACKUP_COUNT = 30

    LOG_CONFIG_DICT = {
        'version': 1,
        'disable_existing_loggers': False,
        # 格式化器
        'formatters': {
            # 简单模式, console专用
            'simple': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(levelname)s %(name)s %(filename)s %(module)s %(funcName)s '
                          '%(lineno)d %(thread)d %(threadName)s %(process)d %(processName)s %(message)s'
            },
            # json模式, 方便ELK收集处理
            'json': {
                'class': 'logging.Formatter',
                'format': '{"time:":"%(asctime)s","level":"%(levelname)s","logger_name":"%(name)s",'
                          '"file_name":"%(filename)s","module":"%(module)s","func_name":"%(funcName)s",'
                          '"line_number":"%(lineno)d","thread_id":"%(thread)d","thread_name":"%(threadName)s",'
                          '"process_id":"%(process)d","process_name":"%(processName)s","message":"%(message)s"}'}
        },
        # 过滤器
        'filters': {
            'info_filter': {
                '()': InfoFilter
            },
            'error_filter': {
                '()': ErrorFilter
            }
        },
        # 处理器
        'handlers': {
            # 控制台输出
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple'
            },
            # info文件输出
            'info_file': {
                'level': 'INFO',
                'formatter': 'json',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': '{0}/{1}_info.log'.format(LOG_PATH, SERVICE_NAME),
                'when': LOG_SPLIT_TYPE,
                'interval': LOG_SPLIT_INTERVAL,
                'encoding': 'utf8',
                'backupCount': LOG_BACKUP_COUNT,
                'filters': ['info_filter']
            },
            # error文件输出
            'error_file': {
                'level': 'ERROR',
                'formatter': 'json',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': '{0}/{1}_error.log'.format(LOG_PATH, SERVICE_NAME),
                'when': LOG_SPLIT_TYPE,
                'interval': LOG_SPLIT_INTERVAL,
                'encoding': 'utf8',
                'backupCount': LOG_BACKUP_COUNT,
                'filters': ['error_filter']
            }
        },
        # 记录器
        'loggers': {
            'full_logger': {
                'handlers': ['console', 'info_file', 'error_file'],
                'level': 'INFO'
            },
            'only_console_logger': {
                'handlers': ['console'],
                'level': 'INFO'
            },
            'only_file_logger': {
                'handlers': ['info_file', 'error_file']
            }
        }
    }

    logging.config.dictConfig(LOG_CONFIG_DICT)

    @classmethod
    def get_logger(cls, logger_name='full_logger') -> logging.Logger:
        if logger_name in ("full_logger", "only_console_logger", "only_file_logger"):
            if cls.logger_instance.get(logger_name):
                return cls.logger_instance[logger_name]
            else:
                cls.logger_instance[logger_name] = logging.getLogger(logger_name)
                return cls.logger_instance[logger_name]
        else:
            cls.logger_instance['full_logger'] = logging.getLogger('full_logger')
            return cls.logger_instance['full_logger']


# if __name__ == "__main__":
#     lo: logging.Logger = LogFactory.get_logger('full_logger')
#     lo.info("haha")
#     lo.error("ai")
