FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py /app/server.py

RUN mkdir -p /app/data /app/plots && \
    chmod -R 777 /app/data /app/plots

EXPOSE 8765

CMD ["python", "server.py"]
