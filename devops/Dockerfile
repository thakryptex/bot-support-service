FROM python:3.7

WORKDIR /app

ADD src/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src/ .

RUN  python manage.py collectstatic --noinput

CMD  ['/bin/sh','-c','python manage.py migrate --noinput && python cherry.py']
