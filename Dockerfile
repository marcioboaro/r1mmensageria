FROM python:3.9-slim-buster

WORKDIR /usr/src/app
ENV TZ=America/Sao_Paulo
#COPY ./requirements.txt ./

RUN pip install -U setuptools
RUN pip install -U wheel
RUN pip install sqlalchemy
RUN pip install pydantic
RUN pip install fastapi
RUN pip install PyMySQL
RUN pip install Pika
RUN pip install uvicorn[standard]
RUN pip install PyJWT
RUN pip install passlib
RUN pip install cryptography
RUN pip install requests
RUN apt-get update && \
    apt-get install -y nano vim && \
    rm -fr /var/lib/apt/lists/*
#RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD [ "uvicorn", "app:app", "--host=0.0.0.0", "--reload" ]
