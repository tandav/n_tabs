FROM python:3-alpine

RUN pip install fastapi uvicorn

EXPOSE 5002

COPY server.py /app/

WORKDIR /app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5002", "--ssl-certfile", "fullchain.pem", "--ssl-keyfile", "privkey.pem"]
