FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y unzip
# https://oliversi.com/2019/01/07/python-docker-selenium-chrome/
# install google-chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable
#install ChromeDriver
ADD https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
    unzip chromedriver_linux64.zip
ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/chrome

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/
