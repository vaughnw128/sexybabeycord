FROM python:3.10.6-slim
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


RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_SSE2_INSTRUCTIONS --no USE_SSE4_INSTRUCTIONS

RUN pip install poetry
COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
