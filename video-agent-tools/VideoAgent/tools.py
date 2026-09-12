import os.path as osp
import json
import pickle
from encoder import encode_sentences
from utils import compute_cosine_similarity, top_k_indices
import os
import cv2
from database import DataBase
from moviepy.editor import VideoFileClip
import socket
import sys
from io import StringIO
import torch
from InternVid.viclip import get_viclip, retrieve_text, _frame_from_video, frames2tensor, get_vid_feat, get_text_feat_dict
import requests
import numpy as np
import base64
import gc
import threading
from pathlib import Path
from captioning import Captioning
from runtime_config import MODEL_CONFIG, resolve_video_agent_path


model_cfgs = {
    f'viclip-{MODEL_CONFIG.viclip_variant}-internvid-10m-flt': {
        'size': MODEL_CONFIG.viclip_variant,
        'pretrained': Path(MODEL_CONFIG.viclip_checkpoint),
    }
}


class ToolKit:
    # Shared class-level model instances to save GPU memory (1-2GB per instance)
    _shared_viclip = None
    _shared_tokenizer = None
    _shared_model_path = None
    _model_lock = threading.Lock()  # Lock for thread-safe model inference
    _init_lock = threading.Lock()   # Lock for thread-safe initialization

    @classmethod
    def _initialize_shared_model(cls, model_dir: Path):
        cfg = next(iter(model_cfgs.values()))
        model_path = (model_dir / cfg['pretrained']).resolve()
        if (
            cls._shared_model_path is not None
            and cls._shared_model_path != model_path
        ):
            raise RuntimeError(
                "ToolKit shared model was initialized from a different "
                f"path: {cls._shared_model_path}"
            )
        if cls._shared_viclip is None:
            with cls._init_lock:
                if cls._shared_viclip is None:
                    cfg = next(iter(model_cfgs.values()))
                    model = get_viclip(
                        cfg['size'],
                        os.fspath(model_path),
                    )
                    assert(type(model)==dict and model['viclip'] is not None and model['tokenizer'] is not None)
                    cls._shared_viclip = model['viclip'].to("cuda")
                    cls._shared_tokenizer = model['tokenizer']
                    cls._shared_model_path = model_path

    def __init__(
        self,
        video_path,
        base_dir='preprocess',
        vqa_tool='videollava',
        use_reid=True,
        captioning: Captioning=None,
        videollava_runtime_dir=None,
        model_dir=None,
    ):
        self.video_path = video_path
        base_name = os.path.basename(video_path).replace(".mp4", "")
        self.video_dir = os.path.join(base_dir, base_name)
        if vqa_tool != "videollava":
            raise ValueError("Only local Video-LLaVA VQA is supported")
        self.vqa_tool = vqa_tool
        if self.vqa_tool == "videollava":
            if videollava_runtime_dir is None:
                raise ValueError(
                    "videollava_runtime_dir is required for videollava"
                )
            runtime_dir = os.fspath(videollava_runtime_dir)
            if not osp.isabs(runtime_dir) or not osp.isdir(runtime_dir):
                raise NotADirectoryError(
                    "videollava_runtime_dir must be an existing absolute "
                    f"directory: {runtime_dir}"
                )
            self.videollava_runtime_dir = runtime_dir
        cap = cv2.VideoCapture(video_path)
        self.fps = round(cap.get(cv2.CAP_PROP_FPS))
        cap.release()
        self.captioning = captioning
        self.model_dir = Path(
            model_dir
            if model_dir is not None
            else resolve_video_agent_path("tool_models")
        )
        if not self.model_dir.is_absolute():
            raise ValueError(f"model_dir must be absolute: {self.model_dir}")
        if not self.model_dir.is_dir():
            raise NotADirectoryError(
                f"model_dir must reference a directory: {self.model_dir}"
            )

        
        with open(osp.join(self.video_dir, 'captions.json')) as f:
            captions = json.load(f)
        self.segments = list(captions.keys())
        self.captions = list(captions.values())
        self.segment_num = len(self.segments)
        self.database = DataBase(
            video_path,
            base_dir=base_dir,
            use_reid=use_reid,
            model_dir=self.model_dir,
        )

        # Initialize shared model if not already done, then reference it
        self._initialize_shared_model(self.model_dir)
        self.viclip = self._shared_viclip
        self.tokenizer = self._shared_tokenizer

        # store the captioning model
        self.captioning = captioning


    def query_database(self, program):
        res = self.database.query_database(program=program)
        return str(res)
    

    def retrieve_candidate_objects(self, description):
        res = self.database.retrieve_candidate_objects(description=description)
        return str(res)


    def caption_retrieval(self, start_segment, end_segment):
        d = f"There are {self.segment_num} segments in total, ranging from 0 to {self.segment_num-1}. "

        start_segment = max(start_segment, 0)
        end_segment = min(end_segment, self.segment_num-1)

        if start_segment > end_segment:
            return d+"Invalid start and end segment IDs!"
        
        caption_start_frame: str = self.segments[start_segment]
        parts = caption_start_frame.split('_')
        caption_start_frame = int(parts[0])
        
        caption_end_frame: str = self.segments[end_segment]
        parts = caption_end_frame.split('_')
        caption_end_frame = int(parts[1])

        res, prompt_tokens, completion_tokens = self.captioning.generate_captions_for_frames(self.video_path, caption_start_frame, caption_end_frame)
        
        # res = dict()
        # for segment_id in range(start_segment, end_segment+1):
        #     res[segment_id] = self.captions[segment_id]
        print(f"Tokens used - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {prompt_tokens + completion_tokens}, for video : {self.video_dir}, caption: {start_segment}-{end_segment}")

        return f'{d}Caption of segments from {start_segment} to {end_segment} is {str(res)}'


    def segment_localization(self, description, k=5):
        with open(osp.join(self.video_dir, 'segment_textual_embedding.pkl'), 'rb') as f:
            segment2textual_emb = pickle.load(f)
        des2textual_emb = encode_sentences(
            sentence_list=[description],
            model_name='clip',
            model_dir=self.model_dir,
        )
        textual_scores = compute_cosine_similarity(target_embedding=des2textual_emb, embedding_list=segment2textual_emb)

        # Explicitly delete large embedding array after use (can be 100MB-1GB)
        del segment2textual_emb
        del des2textual_emb

        with open(osp.join(self.video_dir, 'segment_visual_embedding.pkl'), 'rb') as f:
            segment2visual_emb = pickle.load(f)

        # Thread-safe model inference with lock
        print(f'Getting viclip model')
        # with self._model_lock:
        with torch.no_grad():
            des2visual_emb = self.viclip.get_text_features(description, self.tokenizer, {}).cpu().numpy()
        print(f'Done getting viclip model')
        #print(des2visual_emb.shape)
        visual_scores = compute_cosine_similarity(target_embedding=des2visual_emb, embedding_list=segment2visual_emb)

        # Explicitly delete large embedding arrays after use (can be 100MB-1GB)
        del segment2visual_emb
        del des2visual_emb

        #print(visual_scores)
        #print(textual_scores)
        ensemble_scores = 18*visual_scores +11*textual_scores
        k_indices = top_k_indices(ensemble_scores, k)
        candidate_segment2caption = dict()
        for idx in k_indices:
            candidate_segment2caption[idx] = self.captions[idx]
        res = f"There are {self.segment_num} segments in total, ranging from 0 to {self.segment_num-1}. The most relevant segments are: {candidate_segment2caption}."

        del textual_scores
        del visual_scores
        del ensemble_scores

        return res
    

    def videollava_VQA(self, question, segment_id):
        #print(segment_id, self.segment_num)
        if segment_id not in range(self.segment_num):
            return f"Segment ID {segment_id} not in range 0-{self.segment_num-1}."
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(
            osp.join(self.videollava_runtime_dir, "vqa.sock")
        )
        content_file = osp.join(
            self.videollava_runtime_dir,
            "content.pkl",
        )
        video_segment_path = osp.join(self.video_dir, f'segment_{segment_id}.mp4')
        print(f'video segment path: {video_segment_path}')
        if not osp.exists(video_segment_path):
            #create segment mp4 video
            candidate_segments = []
            print(f'Segmenting1 video at path: {self.video_path} and {video_segment_path}')
            for i in range(segment_id-1, segment_id+2):
                if i < 0 or i > self.segment_num-1:
                    continue
                candidate_segments.append(i)
            segment_start_second = candidate_segments[0]*2
            segment_end_second = (candidate_segments[-1]+1)*2
            print(f'Segmenting2 video at path: {self.video_path} and {video_segment_path}')
            original_stdout = sys.stdout
            output_catcher = StringIO()
            # sys.stdout = output_catcher
            video = VideoFileClip(self.video_path)
            segment_video = video.subclip(segment_start_second, segment_end_second)
            print(f'Segmenting3 video at path: {self.video_path} and {video_segment_path}')
            segment_video.write_videofile(video_segment_path)
            # sys.stdout = original_stdout

            # CRITICAL: Close VideoFileClip objects to prevent massive memory leak
            # Each unclosed clip can hold 500MB-2GB of decoded video data
            segment_video.close()
            video.close()
            del segment_video
            del video
            gc.collect()

        content = dict()
        content['video_path'] = video_segment_path
        content['question'] = question
        with open(content_file, 'wb') as f:
            pickle.dump(content, f)
        client.send(b'sent')
        res = client.recv(1024).decode('utf-8')
        with open(content_file, 'rb') as f:
            ans = pickle.load(f)
        client.send(b'finish')

        # Close socket to prevent resource leak
        client.close()

        return ans
    

    def visual_question_answering(self, question, segment_id):
        return self.videollava_VQA(question=question, segment_id=segment_id)


    def cleanup(self):
        """Explicitly release all instance-specific resources to prevent memory leaks.
        Note: Shared model resources (viclip, tokenizer) are NOT deleted as they are shared across instances."""

        # Just clear instance references to shared models (don't delete the shared models themselves)
        self.viclip = None
        self.tokenizer = None

        # Delete database (contains large pickle data)
        if hasattr(self, 'database') and self.database is not None:
            del self.database
            self.database = None

        # Delete large data structures
        if hasattr(self, 'captions') and self.captions is not None:
            del self.captions
            self.captions = None

        if hasattr(self, 'segments') and self.segments is not None:
            del self.segments
            self.segments = None

        # Force garbage collection (don't clear CUDA cache as shared model is still there)
        # gc.collect()
