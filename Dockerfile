FROM python:3.12.2


RUN mkdir backend
WORKDIR /backend
COPY requirements.txt /backend/
RUN pip install -r requirements.txt 

COPY app/ /backend/app/

EXPOSE 8000 

CMD ["python3", "app/startup_service.py"]