FROM python:3
WORKDIR /opt/
COPY requirements.txt ./
RUN  apt-get update \
    && apt-get install ca-certificates && pip install --no-cache-dir -r requirements.txt\
    && ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo Europe/Moscow > /etc/timezone
COPY main.py ./
ENTRYPOINT ["python", "main.py"]
