FROM python:3.12.2-bookworm
WORKDIR /bot

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ffmpeg \
        libmagic-dev \
        libmagickwand-dev \
        docker.io


RUN pip install poetry
COPY . .

RUN poetry install

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
