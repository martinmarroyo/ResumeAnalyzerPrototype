FROM python:3.11

WORKDIR /app/src

RUN apt-get update && apt-get upgrade -y && \
    apt install weasyprint -y
# Copy the requirements file into the container
COPY requirements.txt requirements.txt

COPY src /app/src
# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]