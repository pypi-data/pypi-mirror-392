FROM raoulgrouls/torch-python-slim:py3.12-torch2.8.0-arm64-uv0.9.8

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

CMD ["streamlit", "run", "src/main.py", "--server.port=8000", "--server.address=0.0.0.0"]