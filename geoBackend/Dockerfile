FROM python:3.9-slim

WORKDIR /app 

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p logs

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app.py"]
