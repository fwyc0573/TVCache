import json
import openai
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import os
from PIL import Image
import clip
import torch
from openai import OpenAI
import torchvision.transforms as T
from PIL import Image
from time import time
from pathlib import Path
from runtime_config import MODEL_CONFIG, resolve_video_agent_path


sentence_models = ['text-embedding-ada-002', 'text-embedding-3-large', 'all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'clip']


def encode_sentences(sentence_list, model_name, model_dir=None):
    '''given a list of sentences, return the embeddings for them using the sentence encoder model'''
    assert model_name in sentence_models
    emb_list = []
    if model_name in['text-embedding-ada-002', 'text-embedding-3-large']: #openai embedding requires api-key
        client = OpenAI()
        emb = client.embeddings.create(input=sentence_list, model=model_name)
        for i in range(len(sentence_list)):
            emb_list.append(np.array(emb.data[i].embedding).reshape(1, -1))
        emb_list = np.concatenate(emb_list, axis=0)
        return emb_list
    elif model_name == 'clip': # clip embedding
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_root = Path(
            model_dir
            if model_dir is not None
            else resolve_video_agent_path("tool_models")
        )
        clip_path = model_root / "CLIP" / MODEL_CONFIG.clip_checkpoint
        if not clip_path.is_file():
            raise FileNotFoundError(
                f"local CLIP checkpoint is required: {clip_path}"
            )
        model, transform = clip.load(str(clip_path), device=device)
        with torch.no_grad():
            for sentence in sentence_list:
                emb_list.append(model.encode_text(clip.tokenize([sentence]).to(device)).cpu().numpy())
        emb_list = np.concatenate(emb_list, axis=0)
        return emb_list
    else: #sentence transformer encoder
        model = SentenceTransformer('sentence-transformers/'+model_name)
        num = len(sentence_list)
        batch_size = 10
        batch_num = num // batch_size
        with torch.no_grad():
            for batch_id in range(batch_num):
                batch_sentences = sentence_list[batch_id*10: (batch_id+1)*10]
                emb_list.append(model.encode(batch_sentences))
            if batch_num * 10 < num: #remaining <10 sentences
                remaining_sentences = sentence_list[batch_num*10: num]
                emb_list.append(model.encode(remaining_sentences))
        return emb_list


if __name__ == '__main__':
    encode_sentences(['hello!', 'what'], model_name='text-embedding-ada-002')
