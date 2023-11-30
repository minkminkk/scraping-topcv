FROM python:3.12-slim-bookworm

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install required Python libraries
COPY ./requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

# Copy src project files
COPY ./src /crawler

# Change workdir
WORKDIR /crawler

# Entrypoint
ENTRYPOINT ["python", "main.py"]