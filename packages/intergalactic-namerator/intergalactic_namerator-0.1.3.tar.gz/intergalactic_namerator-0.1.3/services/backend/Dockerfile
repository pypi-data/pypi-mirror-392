FROM raoulgrouls/torch-python-slim:py3.12-torch2.8.0-arm64-uv0.9.8

WORKDIR /app

RUN uv init
RUN uv add fastapi --extra standard intergalactic-namerator tokenizers loguru

COPY app.py .

EXPOSE 443

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "443"]