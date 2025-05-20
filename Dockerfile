# Use a minimal official Python base image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Copy project files
COPY wan_ip_monitor.py ./
COPY requirements.txt ./

RUN touch /ip.txt
RUN ln -s /ip.txt /app/ip.txt

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Default command
CMD ["python", "wan_ip_monitor.py"]
