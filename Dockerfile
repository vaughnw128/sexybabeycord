FROM python:3.10.12-slim
WORKDIR /bot

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
        make \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libffi-dev \
        liblzma-dev \
        git \
        ffmpeg \
        cmake \
        libmagic-dev \
        libmagickwand-dev \
        libx11-dev \
        libgtk-3-dev \
        libboost-dev \
        libavdevice-dev \
        libavfilter-dev \
        libavformat-dev \
        libavcodec-dev \
        libswresample-dev \
        libswscale-dev \
        libavutil-dev \
        libopenblas-dev \
        liblapack-dev

RUN pip install poetry yt-dlp
COPY pyproject.toml poetry.lock ./

RUN poetry self add poetry-dotenv-plugin
RUN poetry install

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
