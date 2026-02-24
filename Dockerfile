FROM python:3.10-slim

WORKDIR /app

# Copy source and install as editable package.
COPY . /app
RUN pip install --no-cache-dir -e .

EXPOSE 8000 9000

