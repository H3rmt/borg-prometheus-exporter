FROM python:bookworm
# RUN apk add pkgconf openssl-dev fuse-dev gcc
RUN apt update && apt install -y libfuse-dev libacl1-dev

RUN mkdir /.config /.cache && chmod 777 /.config /.cache

COPY ./requirements.txt /requirements.txt
RUN python -m venv prod test && chmod +x ./prod/bin/activate && ./prod/bin/activate && pip install -r /requirements.txt

COPY ./borg-prometheus-exporter.py /borg-prometheus-exporter.py
ENTRYPOINT ["/usr/local/bin/python", "/borg-prometheus-exporter.py"]