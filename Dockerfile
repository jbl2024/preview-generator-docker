FROM python:3.7

RUN apt-get update -y
RUN apt-get install -y zlib1g-dev libjpeg-dev python3-pythonmagick inkscape xvfb poppler-utils libfile-mimeinfo-perl qpdf libimage-exiftool-perl ufraw-batch ffmpeg
RUN pip install preview-generator
RUN apt-get -y install libreoffice
RUN pip install weasyprint gunicorn flask
RUN mkdir /api
WORKDIR /api
ADD ./wsgi.py /api
CMD gunicorn --bind 0.0.0.0:5001 wsgi:app
