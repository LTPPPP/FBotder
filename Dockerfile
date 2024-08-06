# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.9

# Set the working directory.
WORKDIR /app

# Copy the current directory contents into the container at /app.
COPY . /app

# Install any needed packages specified in requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container.
EXPOSE 5000

# Define environment variable.
ENV NAME World

# Run app.py when the container launches.
CMD ["python", "geminiBot.py"]
