import subprocess
# worker -l INFO 
CELERY_COMMAND = "celery -A app.celery worker -E -l INFO"
UVICORN_COMMAND = "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

def start_celery():
    celery_process = subprocess.Popen(CELERY_COMMAND.split())
    return celery_process

def start_uvicorn():
    uvicorn_process = subprocess.Popen(UVICORN_COMMAND.split())
    return uvicorn_process

if __name__ == "__main__":
    celery_process = start_celery()
    uvicorn_process = start_uvicorn()

    try:
        # Keep processes running (wait for termination)
        celery_process.wait()
        uvicorn_process.wait()
    except KeyboardInterrupt:
        celery_process.terminate()
        uvicorn_process.terminate()
