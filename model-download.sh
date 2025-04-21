#!/bin/bash

# This script downloads the Mistral model for LocalAI

# Create models directory if it doesn't exist
mkdir -p models

echo "Downloading Mistral model for LocalAI..."
echo "This might take a while depending on your internet connection."

# You can replace this with a different model if preferred
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_FILE="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# Download the model
curl -L -o "$MODEL_FILE" "$MODEL_URL"

# Create model config file for LocalAI
cat > models/mistral.yaml << EOL
name: mistral
parameters:
  model: mistral-7b-instruct-v0.2.Q4_K_M.gguf
  temperature: 0.7
  top_p: 0.9
  context_size: 8192
  stop:
    - "HUMAN:"
    - "ASSISTANT:"
template:
  completion: |
    <s>{{.Input}}</s>
  chat: |
    <s>{{if .System}}[INST] {{.System}} {{end}}{{range $i, $message := .Messages}}{{if eq $message.Role "user"}}{{if eq $i 0}}[INST] {{else}}[INST] {{end}}{{$message.Content}} [/INST]{{else}}{{$message.Content}}{{end}}{{end}}
EOL

echo "Model download complete!"
echo "You can now run the application with: docker-compose up -d"
