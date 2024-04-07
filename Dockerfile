# Use the official Python base image
FROM python:3.12.2-alpine3.19

ENV GITHUB_REPO_URL=""
ENV GITHUB_USERNAME=""
ENV GITHUB_EMAIL=""

# Set the working directory in the container
WORKDIR /app

RUN apk add --no-cache git && rm -rf /var/cache/apk/*

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY init.py .

# Set the entrypoint command for the container
CMD ["python", "init.py"]