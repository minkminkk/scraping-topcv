FROM python:3.12-alpine

# Set working directory
WORKDIR /src

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install required Python libraries
COPY ./src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy src project files
COPY ./src ./crawler

# Entrypoint
ENTRYPOINT ["python", "crawler/main.py"]