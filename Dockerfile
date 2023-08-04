FROM ubuntu:22.04 as base

WORKDIR /

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
        libmagickwand-dev

RUN git clone https://github.com/pyenv/pyenv.git /pyenv
ENV PYENV_ROOT /pyenv
RUN /pyenv/bin/pyenv install 3.10.6
RUN /pyenv/bin/pyenv global 3.10.6
RUN eval "$(/pyenv/bin/pyenv init -)" && /pyenv/bin/pyenv local 3.10.6 && pip install numpy poetry setuptools wheel six auditwheel


WORKDIR /bot
COPY pyproject.toml poetry.lock ./

RUN mkdir -p .venv
RUN eval "$(/pyenv/bin/pyenv init -)" && /pyenv/bin/pyenv local 3.10.6 && poetry config virtualenvs.in-project true --local && poetry install

COPY . .

ENTRYPOINT ["sh"]
CMD ["entrypoint.sh"]
