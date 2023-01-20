FROM python:3.11.0rc2-alpine3.16

WORKDIR /app
COPY intercept.py /app/intercept.py
COPY requirements.txt /app/requirements.txt
RUN mkdir /outdata
RUN pip3 install -r requirements.txt --no-cache

ENV UDADO_IN_FOLDER='/outdata'

CMD [ "python3", "intercept.py" ]