FROM python:3.10.6

WORKDIR /bot
COPY pyproject.toml poetry.lock ./

RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip3 install cmake

RUN git clone https://github.com/davisking/dlib.git
RUN cmake ./dlib; cmake --build .

RUN pip3 install poetry
RUN poetry self add poetry-dotenv-plugin
RUN poetry install

COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
