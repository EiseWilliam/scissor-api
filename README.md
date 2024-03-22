# URL Shortener

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

