FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

ARG USERNAME=vscode
RUN useradd --create-home --shell /bin/bash $USERNAME \
    && mkdir -p /workspaces \
    && chown -R $USERNAME:$USERNAME /workspaces

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/project

# Hugging Face stack + 4-bit quantization support
RUN pip install --no-cache-dir \
    transformers \
    accelerate \
    datasets \
    bitsandbytes \
    sentencepiece \
    trl peft

# If your project has its own requirements.txt, uncomment:
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

USER $USERNAME