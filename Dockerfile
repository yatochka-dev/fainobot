#
FROM python:3.10

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

COPY ./prisma /code/prisma

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN prisma generate
RUN prisma db push

#
COPY . /code/

ENV TESTING=false
#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]