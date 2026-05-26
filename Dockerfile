FROM python:3.11-slim

WORKDIR /app

# Install curl and ca-certificates to fetch the binary securely
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install fastmcp
RUN pip install --no-cache-dir fastmcp

# Dynamically download the OPA binary based on the current architecture
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then OPA_ARCH="amd64"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then OPA_ARCH="arm64"; \
    else echo "Unsupported architecture: $ARCH" && exit 1; fi && \
    curl -L -o opa "https://openpolicyagent.org/downloads/latest/opa_linux_${OPA_ARCH}"

RUN chmod 755 ./opa

# Copy your server script
COPY server.py .
COPY policy_skill.md .

# Run the script when the container starts
ENTRYPOINT ["python", "server.py"]