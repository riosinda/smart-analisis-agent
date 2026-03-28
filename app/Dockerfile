FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /project

# Build deps required by pycairo (pulled in by xhtml2pdf -> svglib -> rlpycairo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libcairo2-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Cache dependency layer — copy only pyproject before source
COPY app/pyproject.toml /project/app/pyproject.toml

RUN cd /project/app && uv pip install --system .

# Copy source code and data
COPY app/ /project/app/
COPY data/ /project/data/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
