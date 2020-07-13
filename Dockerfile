FROM daocloud.io/crediteaseitsec/centos_py37

RUN mkdir -p /app/insight2
ADD . /app/insight2/
RUN pip install -r /app/insight2/requirements.txt -i https://mirrors.aliyun.com/pypi/simple

WORKDIR /app/insight2

