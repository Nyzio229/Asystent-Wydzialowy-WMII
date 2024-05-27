#!/bin/bash
set -e

MODEL_NAME=vicuna-13b-v1.5-16k

MODEL_PATH=$(pwd)/models/$MODEL_NAME

huggingface-cli download lmsys/$MODEL_NAME --local-dir $MODEL_PATH

git clone https://github.com/ggerganov/llama.cpp.git || true

cd llama.cpp

pip install -r requirements.txt

make

GGML_MODEL_NAME=ggml-f16
GGML_MODEL_PATH=$MODEL_PATH/$GGML_MODEL_NAME.gguf

python convert.py $MODEL_PATH --outfile $GGML_MODEL_PATH

QUANTIZATION=Q8_0
QUANTIZED_MODEL_PATH=$MODEL_PATH/$GGML_MODEL_NAME-$QUANTIZATION.gguf

./quantize $GGML_MODEL_PATH $QUANTIZED_MODEL_PATH $QUANTIZATION