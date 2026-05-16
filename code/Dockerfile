FROM ubuntu:22.04

# Update package lists and install prerequisites
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    ffmpeg \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install NVIDIA Container Toolkit
RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
       sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
       tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
    && apt-get update \
    && apt-get install -y nvidia-container-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Configure Docker runtime for NVIDIA
RUN nvidia-ctk runtime configure --runtime=docker

# Set environment variables
ENV port=662
EXPOSE $port
WORKDIR /home/code/

# Copy and install Python dependencies
COPY app.py /home/code/
COPY requirements.txt /home/code/
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the application with Uvicorn
CMD uvicorn app:app --host 0.0.0.0 --port $port --timeout-keep-alive 600