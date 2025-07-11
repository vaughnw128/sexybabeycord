FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ffmpeg \
        libmagic-dev \
        libmagickwand-dev \
        docker.io

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/python3", "tracing.py"]