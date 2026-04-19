FROM debian:bullseye-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    bash \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install grpcurl
RUN wget -O grpcurl.tar.gz https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_64.tar.gz && \
    tar -xzf grpcurl.tar.gz -C /usr/local/bin grpcurl && \
    rm grpcurl.tar.gz

COPY wait-for-it.sh /usr/local/bin/wait-for-it
COPY init-fixtures.sql init-fixtures-booking.sql regress.sh ./
RUN chmod +x /usr/local/bin/wait-for-it regress.sh

ENTRYPOINT ["./regress.sh"]
