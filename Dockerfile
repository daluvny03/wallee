# Gunakan base image Python resmi yang ringan
FROM python:3.9-slim

# Tentukan working directory di dalam container
WORKDIR /code

# Salin file requirements.txt
COPY ./requirements.txt /code/requirements.txt

# Install dependencies tanpa menyimpan cache untuk menghemat ruang disk
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Salin seluruh isi direktori project ke dalam container
COPY . /code

# Pastikan direktori models ada dan berikan izin akses tulis/baca penuh
RUN mkdir -p /code/models && chmod -R 777 /code/models

# Expose port 7860 (Hugging Face Spaces mewajibkan aplikasi mendengarkan port ini)
EXPOSE 7860

# Jalankan server uvicorn pada port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
