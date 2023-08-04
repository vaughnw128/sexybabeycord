FROM ubuntu:22.04 as base

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

RUN apt-get install -y python3-pip

COPY pyproject.toml poetry.lock ./

# RUN pip3 install cmake
# RUN git clone https://github.com/davisking/dlib.git
# RUN cmake ./dlib; cmake --build .

RUN pip3 install poetry

RUN eval "$(/pyenv/bin/pyenv init -)" && /pyenv/bin/pyenv local 3.10.6 && poetry config virtualenvs.in-project true --local && poetry install

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
