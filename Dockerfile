# set base image (host OS)
FROM python:3.9
ENV PYTHONUNBUFFERED=1

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt /code/


# COPY /usr/local/Cellar/gdal/3.4.1_1/lib/libgdal.dylib /code/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# copy the content of the local src directory to the working directory
COPY . /code/