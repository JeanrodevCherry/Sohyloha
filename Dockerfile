#--------------------------------------------#
#-------------  BASE IMAGE  -----------------#
#--------------------------------------------#
FROM python:3.11.14-bookworm AS BASE

WORKDIR /app
COPY ./requirements.txt app/requirements.txt
RUN ls -l /app/
RUN apt update && apt upgrade -y && pip install -r ./app/requirements.txt
#---------------------------------------------