FROM python:3.11.5
WORKDIR /bot

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ffmpeg \
        libmagic-dev \
        libmagickwand-dev \
        docker.io


RUN pip install poetry yt-dlp
COPY pyproject.toml poetry.lock ./

RUN poetry install
USER sexybabeycord:sexybabeycord

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
