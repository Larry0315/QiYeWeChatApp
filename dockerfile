FROM python:3.6

RUN pip3 install aiohttp aiomysql ujson uvloop aiofiles \
                 aiohttp-swagger pycrypto gunicorn \
                 -i https://mirrors.aliyun.com/pypi/simple

COPY robot robot

WORKDIR /robot/

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

CMD ["gunicorn", "-c", "gunicorn.conf", "main:web_app"]