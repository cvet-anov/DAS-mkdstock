FROM python:3.9-slim

WORKDIR /analysis_service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5003
CMD ["python", "app.py"]