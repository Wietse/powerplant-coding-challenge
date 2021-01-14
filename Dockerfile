FROM python:3.9.1-slim-buster

RUN apt-get update && apt-get install -y \
    g++

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade setuptools pip wheel

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /app
RUN pip install -e /app

WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "--config=/app/gunicorn_conf.py", "pcc.webapp:create_app()"]


# vim: ft=dockerfile
