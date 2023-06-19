# Backend with FastAPI

This Backend is based on [FastAPI](https://fastapi.tiangolo.com/), PostgreSQL with [sqlmodel](https://sqlmodel.tiangolo.com/) and Tensorflow.

## Setup

Get environment variables:
```bash
cp example.env .env
```

### Setup SSL
Install mkcert. Installation instructions can be found here: https://github.com/FiloSottile/mkcert   
Create certificates by running the following command in the frontend folder:   
```bash
mkcert localhost
```
Update `docker-compose.yml`:
```bash
command: uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile localhost-key.pem --ssl-certfile localhost.pem --reload
```

### Build and start containers:

```bash
docker-compose up -d
```

FastAPI: http://localhost:8000/   
FastAPI Docs: http://127.0.0.1:8000/docs   
Adminer: http://localhost:8080/   
