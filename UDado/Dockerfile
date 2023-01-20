FROM coinor/coin-or-optimization-suite

RUN apt-get update
RUN apt-get install -y libffi-dev libc-dev python3-dev python3-pip
WORKDIR /app
RUN mkdir /indata
RUN touch /indata/input.json
RUN mkdir /outdata
COPY *.py /app/
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt --no-cache

CMD ["python3", "udado.py", "-i", "/indata/input.json", "-o", "/outdata/solution.txt", "--trep", "/outdata/timing.csv"]
