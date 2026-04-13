FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto file and regenerate Python files with correct version
COPY booking.proto .
RUN pip install protobuf==4.25.3 grpcio-tools==1.62.1 && \
    python -m grpc_tools.protoc --python_out=. --grpc_python_out=. --proto_path=. booking.proto

# Copy the rest of the application code
COPY *.py .

# Expose the gRPC port
EXPOSE 9090

# Start the gRPC server
CMD ["python", "main.py"]