# -------- Stage 1: Build Layer --------
FROM --platform=linux/amd64 python:3.11-slim AS builder

WORKDIR /app

RUN echo "[Build] Updating apt and installing build dependencies..."

COPY requirements.txt .

RUN echo "[Build] Installing Python dependencies..."
#RUN pip install --no-cache-dir --upgrade pip && \
    RUN pip install --no-cache-dir -r requirements.txt

# -------- Stage 2: Final Image --------
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

RUN echo "[Runtime] Preparing runtime environment..."

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

RUN mkdir -p /app/input /app/output
RUN chmod +x main_modular.py

ENV PYTHONPATH=/app \
    TORCH_DEVICE=cpu \
    NO_CUDA=1

VOLUME ["/app/input", "/app/output"]

RUN echo "[Runtime] Image build complete. Ready to run."

CMD ["python", "main_modular.py"]
