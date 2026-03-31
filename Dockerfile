# Python 3.11 asosiy image
FROM python:3.11-slim

# Ishchi papka
WORKDIR /app

# System tools kerak bo‘lsa o‘rnatish (build-essential va curl)
RUN apt-get update && apt-get install -y build-essential curl git && rm -rf /var/lib/apt/lists/*

# Rust kerak bo‘lsa (pydantic-core uchun)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# requirements.txt ni copy va pip upgrade
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Bot fayllarini copy qilish
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]