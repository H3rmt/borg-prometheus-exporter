FROM python:slim-bookworm AS build
WORKDIR /app
# RUN apk add pkgconf openssl-dev fuse-dev gcc
RUN apt update && apt install -y libssl-dev libfuse-dev libacl1-dev pkgconf build-essential

RUN mkdir /.config /.cache && chmod 777 /.config /.cache

COPY ./requirements.txt /requirements.txt
ENV PATH="/app/prod/bin:$PATH"
ENV VIRTUAL_ENV="/app/prod/"
RUN python -m venv prod && /app/prod/bin/pip install -r /requirements.txt

FROM python:slim-bookworm AS run
WORKDIR /app
ENV PATH="/app/prod/bin:$PATH"
ENV VIRTUAL_ENV="/app/prod/"
COPY ./borg-prometheus-exporter.py /app/borg-prometheus-exporter.py
COPY --from=build /app/prod /app/prod
ENTRYPOINT ["python", "/app/borg-prometheus-exporter.py"]