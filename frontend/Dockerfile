FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /project/frontend

# Cache dependency layer
COPY frontend/pyproject.toml /project/frontend/pyproject.toml

RUN uv pip install --system .

# Copy source code
COPY frontend/ /project/frontend/

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
