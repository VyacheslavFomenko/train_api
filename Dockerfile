LABEL maintainer="playfog3@gmail.com"

ENV PYTHONNBUFFERED=1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
