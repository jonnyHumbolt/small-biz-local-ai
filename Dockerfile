# Step 1: Use an official, lightweight Python base image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Step 4: Install ALL libraries listed in requirements.txt (including psycopg2-binary)
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your scripts into the container
COPY app.py .
COPY init_pg_db.py .

# Step 6: Expose the standard Streamlit web port
EXPOSE 8501

# Step 7: Command to boot the dashboard application on container startup
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
