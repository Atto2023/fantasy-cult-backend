FROM python:3.10-slim-buster
ARG ENV
WORKDIR /app
COPY ./requirements.txt .
COPY . /app/
RUN echo "${ENV}" > /app/src/.env
RUN apt-get update
RUN pip install -r ./requirements.txt
EXPOSE 8000
CMD ["uvicorn","--host","0.0.0.0","--port","8000","src.main:app"]