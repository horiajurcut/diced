 FROM python:3
 
 ENV PYTHONUNBUFFERED 1
 
 RUN mkdir /diced
 WORKDIR /diced
 
 ADD requirements.txt /diced/
 RUN pip install -r requirements.txt
 
 ADD diced/ /diced/