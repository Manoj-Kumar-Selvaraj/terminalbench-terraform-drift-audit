FROM python:3.11-slim

WORKDIR /task

COPY . /task

RUN pip install --no-cache-dir pytest==7.4.4 \
    && chmod +x solution.sh run-tests.sh

CMD ["bash", "./run-tests.sh"]
