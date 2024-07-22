FROM python:3.11

WORKDIR /app/src

RUN apt-get update && apt-get upgrade -y && \
    apt install weasyprint -y
# Copy the requirements file into the container
COPY api /app/src
# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]