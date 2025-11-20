#!/bin/bash

set -e  # Exit on error

# Directory structure
PYTHON_OUT_DIR="ara_api_lua"
COMMUNICATION_DIR="_utils/communication"
PROTO_DIR="protobuf"
COMMON_DIR="messages"
GRPC_DIR="grpc"

# Create paths
PROTO_PATH="$PYTHON_OUT_DIR/$COMMUNICATION_DIR/$PROTO_DIR"
OUTPUT_PATH="$PYTHON_OUT_DIR/$COMMUNICATION_DIR/$GRPC_DIR"
COMMON_PROTO_PATH="$PROTO_PATH/$COMMON_DIR"

# Function for generating code from proto files
generate_proto() {
  local proto_file=$1
  echo "  - Processing $proto_file"

  poetry run python3 -m grpc_tools.protoc \
    -I"$PROTO_PATH" \
    --python_out="$OUTPUT_PATH" \
    --grpc_python_out="$OUTPUT_PATH" \
    "$proto_file"

  # Check for error
  if [ $? -ne 0 ]; then
    echo "Error generating code for $proto_file"
    exit 1
  fi
}

# Create output directories
mkdir -p "$OUTPUT_PATH/$COMMON_DIR"

echo "Generating Python code from .proto files..."

# Generate message protos
echo "Generating message definitions:"
for proto in "$COMMON_PROTO_PATH/base_msg.proto" "$COMMON_PROTO_PATH/msp_msg.proto" "$COMMON_PROTO_PATH/nav_msg.proto" "$COMMON_PROTO_PATH/vision_msg.proto"; do
  if [ -f "$proto" ]; then
    generate_proto "$proto"
  else
    echo "  - Skipping $proto (file not found)"
  fi
done

# Generate service protos
echo "Generating service definitions:"
for proto in "$PROTO_PATH/msp.proto" "$PROTO_PATH/navigation.proto" "$PROTO_PATH/vision.proto"; do
  if [ -f "$proto" ]; then
    generate_proto "$proto"
  else
    echo "  - Skipping $proto (file not found)"
  fi
done

# Post-processing to fix imports
echo "Fixing imports in generated files..."
for py_file in $(find "$OUTPUT_PATH" -name "*.py"); do
  echo "  - Fixing imports in $py_file"

  # Fix various import patterns
  sed -i '' -e 's/from messages import/from ara_api_lua._utils.communication.grpc.messages import/g' "$py_file"
  sed -i '' -e 's/from messages\./from ara_api_lua._utils.communication.grpc.messages./g' "$py_file"
  sed -i '' -e 's/import messages\./import ara_api_lua._utils.communication.grpc.messages./g' "$py_file"

  # Fix variable references to messages module
  sed -i '' -e 's/\bmessages_dot_/ara_api_lua._utils.communication.grpc.messages_dot_/g' "$py_file"
done

echo "All proto files processed successfully!"
echo "Output directory: $OUTPUT_PATH"
