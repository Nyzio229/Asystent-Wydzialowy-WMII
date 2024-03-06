from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from qdrant_client import QdrantClient
import numpy as np
import json

app = Flask(__name__)

qdrant_client = QdrantClient(
    url="http://158.75.112.151:6333",
    api_key="MikoAI",
)

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

@app.route('/api/getIndex', methods=['POST'])
def getIndex():

    data = request.json
    if 'data' in data:

        floats = data['data']
        result = qdrant_client.search("asystent_FAQ",floats,limit=3)

        resultSorted = sorted(result, key=lambda x: x.score, reverse=True)
        if (resultSorted[0].score> 0.75):
            out = resultSorted[0].id
        else:
            out = -1
        return jsonify({'output_string': out})
    else:
        return jsonify({'error': 'Input float[] not provided'}), 400
    

@app.route('/api/embedding', methods=['POST'])
def embedding():
    data = request.json
    if 'input_string' in data:
        input_string = data['input_string']

        # Load model from HuggingFace Hub
        tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

        # Tokenize sentences
        encoded_input = tokenizer(input_string, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = model(**encoded_input)

        # Perform pooling
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        sentence_embeddings_list = sentence_embeddings.tolist()
        
        return jsonify({'output_string': sentence_embeddings_list[0]})
    else:
        return jsonify({'error': 'Input string not provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)