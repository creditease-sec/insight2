FROM crediteaseitsec/centos_py3.7:latest

RUN mkdir -p /app/insight2
ADD . /app/insight2/
RUN pip install -r /app/insight2/requirements.txt -i https://mirrors.aliyun.com/pypi/simple

WORKDIR /app/insight2

