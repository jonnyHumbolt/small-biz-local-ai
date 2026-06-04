# Step 1: Use an official, lightweight Python base image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy your python scripts and existing database into the container filesystem
COPY app.py .
COPY init_db.py .
COPY inventory.db .

# Step 4: Install only the specific Python libraries required for the UI layer
RUN pip install --no-cache-dir streamlit ollama

# Step 5: Expose the standard Streamlit web port
EXPOSE 8501

# Step 6: Command to boot the dashboard application on container startup
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
