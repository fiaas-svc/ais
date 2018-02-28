FROM python:alpine
MAINTAINER fiaas@googlegroups.com
COPY . /ais
WORKDIR /ais
RUN pip install .
CMD ["ais"]
