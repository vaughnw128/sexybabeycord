FROM ubuntu:22.04 as base

WORKDIR /bot
COPY pyproject.toml poetry.lock ./

RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN apt-get install -y --no-install-recommends make build-essential libssl-dev wget curl

RUN apt-get install -y git
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv

ENV PYENV_ROOT="$HOME/.pyenv"
ENV PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
RUN pyenv install 3.10.6
RUN pyenv global 3.10.6

RUN pip3 install cmake
RUN git clone https://github.com/davisking/dlib.git
RUN cmake ./dlib; cmake --build .

RUN pip3 install poetry
RUN poetry self add poetry-dotenv-plugin
RUN poetry install

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
