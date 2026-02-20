# 1. Base Image: We start with a lightweight, official Python Linux environment
FROM python:3.10-slim

# 2. Working Directory: Create a folder inside the container to hold our code
WORKDIR /app

# 3. Copy Dependencies: Copy only the requirements file first (optimizes caching)
COPY requirements.txt .

# 4. Install Dependencies: Run pip inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the Code: Copy the rest of our SentinelX project into the container
COPY . .

# 6. Run Uvicorn: The command to start our API when the container boots
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]