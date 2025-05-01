FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# COPY . /app

EXPOSE 8000

CMD [ "fastapi", "dev", "src", "--host", "0.0.0.0" ]
