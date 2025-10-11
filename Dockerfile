FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml .
COPY requirements.txt .
COPY . .

# Create virtual environment and install dependencies
RUN /root/.local/bin/uv venv && /root/.local/bin/uv pip install -r requirements.txt

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application using uv
CMD ["/root/.local/bin/uv", "run", "python", "-m", "app.main"]