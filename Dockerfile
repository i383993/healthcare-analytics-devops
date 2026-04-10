# Use bookworm instead of slim to ensure package availability
FROM python:3.11-bookworm

# Install OpenJDK
RUN apt-get update && \
    apt-get install -y default-jdk --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME dynamically so it never breaks
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="$JAVA_HOME/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
