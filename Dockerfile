FROM python:3.6
ADD ./auth-center.pyz /code/auth-center.pyz
ADD ./requirements/requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt