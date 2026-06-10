# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Buat user baru (Hugging Face Spaces butuh user dengan UID 1000)
RUN useradd -m -u 1000 user
USER user
WORKDIR $HOME/app

# Copy requirements dan install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Download model AI saat build agar startup cepat
COPY --chown=user download_models.py .
RUN python download_models.py

# Copy seluruh kode backend
COPY --chown=user . .

# Expose port (HF Spaces default 7860)
EXPOSE 7860

# Jalankan aplikasi menggunakan uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
