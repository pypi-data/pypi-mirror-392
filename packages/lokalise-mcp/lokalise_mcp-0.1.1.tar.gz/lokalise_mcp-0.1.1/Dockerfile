# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install git (needed for GitPython)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Set environment variables with defaults (can be overridden)
ENV LOKALISE_API_TOKEN="" \
    LOKALISE_PROJECT_ID="" \
    ANTHROPIC_API_KEY="" \
    DEFAULT_BASE_BRANCH="main" \
    DEFAULT_BATCH_SIZE="3" \
    ENABLE_SAFETY_CHECKS="true"

# Run the MCP server
CMD ["python", "-m", "lokalise_mcp.server"]
