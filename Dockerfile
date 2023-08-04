FROM ubuntu:22.04 as base

ENV PYTHON_VERSION 3.10.6

WORKDIR /bot

RUN apt-get -y update
RUN apt-get install -y ffmpeg cmake

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
        git 

RUN git clone https://github.com/pyenv/pyenv.git /pyenv
ENV PYENV_ROOT /pyenv
RUN /pyenv/bin/pyenv install 3.10.6
RUN /pyenv/bin/pyenv global 3.10.6

COPY pyproject.toml poetry.lock ./

# RUN pip3 install cmake
# RUN git clone https://github.com/davisking/dlib.git
# RUN cmake ./dlib; cmake --build .

RUN pip3 install poetry
RUN poetry self add poetry-dotenv-plugin
RUN poetry install

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
