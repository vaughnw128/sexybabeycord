FROM cgr.dev/chainguard/wolfi-base AS builder

RUN apk add --no-cache \
        python-3.14 \
        ffmpeg \
        imagemagick \
        file \
        curl \
        unzip \
        rust

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Deno
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh

WORKDIR /app
COPY . .

ENV NUMBA_CACHE_DIR=/tmp/numba-cache
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    uv sync --frozen

FROM cgr.dev/chainguard/wolfi-base

RUN apk add --no-cache \
        python-3.14 \
        ffmpeg \
        imagemagick \
        file

COPY --from=builder /usr/local/bin/deno /usr/local/bin/deno
COPY --from=builder /app /app

WORKDIR /app
ENV NUMBA_CACHE_DIR=/tmp/numba-cache
ENV DENO_INSTALL=/usr/local
ENV PATH="/app/.venv/bin:/usr/local/bin:$PATH"

CMD ["/app/.venv/bin/sexybabeycord"]
