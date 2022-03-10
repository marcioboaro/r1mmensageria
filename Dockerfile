FROM python:3.10-slim-buster

WORKDIR /usr/src/app

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

#RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8008
CMD [ "uvicorn", "app:app", "--host=0.0.0.0", "--reload" ]
