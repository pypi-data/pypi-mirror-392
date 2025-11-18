FROM ubuntu:24.04

# Install system tools commonly used by Agent Skills and Python
RUN apt-get update && apt-get install -y \
    # PDF processing tools
    poppler-utils \
    qpdf \
    # Office suite
    libreoffice \
    # Image processing
    imagemagick \
    # Standard Unix tools
    findutils \
    coreutils \
    grep \
    sed \
    gawk \
    # Archive tools
    unzip \
    zip \
    tar \
    gzip \
    bzip2 \
    xz-utils \
    # Network tools
    curl \
    wget \
    # Python and pip
    python3 \
    python3-pip \
    python3-venv \
    # Python development tools
    build-essential \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Create a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies directly from requirements
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    httpx>=0.25.0 \
    pydantic>=2.4.0 \
    python-multipart>=0.0.6 \
    pexpect

# Copy application code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV SKILLS_PATH=/skills
ENV WORKSPACE_PATH=/workspace

# Create necessary directories
RUN mkdir -p /skills/public /workspace /tmp

# Set up permissions
RUN chmod 755 /skills /workspace /tmp

# Expose the server port
EXPOSE 8870

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import httpx; httpx.get('http://localhost:8870/api/v1/health', timeout=5)" || exit 1

# Default command
CMD ["python3", "-m", "lyrics.server", "--host", "0.0.0.0", "--port", "8870"]