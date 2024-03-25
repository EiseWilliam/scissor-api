# Scissor URL Shortener

A high-performance URL shortening service built with a modern tech stack for robust functionality and a smooth user experience.

## Technologies
  - [**FastAPI**](https://fastapi.tiangolo.com) - Web framework.
  - [Uvicorn](https://fastapi.tiangolo.com) - HTTP Server.
  - [Pydantic](https://docs.pydantic.dev) - data validation and settings management.
  - [MongoDB](https://www.mongodb.com/) - Data Storage.
  - [Redis](https://redis.io/) - In-memory cache for analytics and rate limiting.
  - [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) - Distributed task queue for background processing e.g fetching Url preview data.

## Features
 - Create short, memorable URLs from long, unwieldy links.
 - Gain detailed analytics on shortened URLs, including clicks, referrers, and location data.
 - Generate QR codes for quick sharing of shortened links.
 - Protected endpoints with robust rate limiting.
 - Dockerized Setup.
 - JWT token authentication.

## Local Setup with Docker
### Prerequisites
- Docker

### Steps
1. Clone the repository
```bash
git clone https://github.com/EiseWilliam/scissor-api 
```
2. Change directory
```bash
cd scissor-api
```
3. Build the docker images
```bash
docker-compose build
```
4. Start the services
```bash
docker-compose up
```
5. Access the API docs at `http://localhost:8000/docs`


#### Optional: Change environment variables

If you want to make changes to environment variables like jwt secret key, you can do so by editing the `envsampledocker` file in the root directory and renaming it to `.env`.

by default all env variables for docker setup is defined in `scissor-api/app/core/config/settings.py` file.

## Local Setup without Docker
### Prerequisites
- Python 3.10
- MongoDB
- Redis

### Steps
1. Clone the repository
```bash
git clone https://github.com/EiseWilliam/scissor-api
```
2. Change directory
```bash
cd scissor-api
```
3. Create a virtual environment
```bash
python3 -m venv venv
```
4. Activate the virtual environment
```bash
source venv/bin/activate
```
5. Install dependencies
```bash
pip install -r requirements.txt
```
6. Environment variables
```bash
cp .envsample .env
```
7. Start the server
```bash
python3 run.py
```
8. Access the API docs at `http://localhost:8000/docs`

## API Documentation
View API documentation at [Scissor API Documentation](https://eisewilliam.stoplight.io/docs/scissor/branches/main/5714202d0c9dc-scissors-api)

