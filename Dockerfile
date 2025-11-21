FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY data/ ./data/
COPY params_example.json ./

# Sync dependencies
RUN uv sync

# Copy startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port for XMPP server (default SPADE port)
EXPOSE 5222

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

