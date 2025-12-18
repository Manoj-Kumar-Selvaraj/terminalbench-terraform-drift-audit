FROM python:3.11-slim

WORKDIR /task

# Copy task contents into container
COPY . /task

# Install required test dependency (pinned for determinism)
RUN pip install --no-cache-dir pytest==7.4.4 \
    && chmod +x solution.sh run-tests.sh

# Default command (docker-compose will invoke this)
CMD ["bash", "./run-tests.sh"]
