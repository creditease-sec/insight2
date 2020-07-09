FROM crediteaseitsec/py2.7_private

RUN mkdir -p /app/insight2
ADD . /app/insight2/

RUN cd /app/insight2 && /app/python/python removepyc.py && /app/python/python -m compileall /app/insight2 && /app/python/python /app/insight2/removepy.py

FROM crediteaseitsec/py2.7_private

COPY --from=0 /app/insight2 /app/insight2
RUN /app/python/python -m pip install -r /app/insight2/requirements.txt -i https://mirrors.aliyun.com/pypi/simple

WORKDIR /app/insight2

