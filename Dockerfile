# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY realtime_translator/requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app/realtime_translator
COPY realtime_translator realtime_translator

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable for Cloud Run
ENV PORT=8080

# Run app.py when the container launches
# Use shell form to expand environment variable
CMD sh -c "uvicorn realtime_translator.app:app --host 0.0.0.0 --port ${PORT}"
