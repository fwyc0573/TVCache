import os
import time
import torch
import json
import cv2
import pickle
from pathlib import Path
from InternVid.viclip import get_viclip, frames2tensor, get_vid_feat
from encoder import encode_sentences
from runtime_config import MODEL_CONFIG, resolve_video_agent_path


model_cfgs = {
    f'viclip-{MODEL_CONFIG.viclip_variant}-internvid-10m-flt': {
        'size': MODEL_CONFIG.viclip_variant,
        'pretrained': Path(MODEL_CONFIG.viclip_checkpoint),
    }
}

class SegmentFeature:
    def __init__(
        self,
        video_path_list,
        base_dir='preprocess',
        model_dir=None,
    ):
        self.video_path_list = video_path_list
        self.base_dir = base_dir
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
        self.seconds_per_feat = 2
        self.frames_per_feat = 10

        start_time = time.time()
        cfg = next(iter(model_cfgs.values()))
        model = get_viclip(
            cfg['size'],
            os.fspath(self.model_dir / cfg['pretrained']),
        )
        assert(type(model)==dict and model['viclip'] is not None and model['tokenizer'] is not None)
        self.clip, tokenizer = model['viclip'], model['tokenizer']
        self.clip = self.clip.to("cuda")

        # Log viCLIP model size in MB
        viclip_size_mb = sum(p.numel() * p.element_size() for p in self.clip.parameters()) / (1024 * 1024)
        print(f'viCLIP Segment Model Size: {viclip_size_mb:.2f} MB')

        end_time = time.time()
        print(f'time for loading viCLIP model: {round(end_time-start_time, 3)} seconds')
       

    def create_textual_embedding(self):
        """use the sentence encoder model to embed the captions of all the videos"""
        model='clip'
        for video_path in self.video_path_list:
            start_time = time.time()
            base_name = os.path.basename(video_path).replace(".mp4", "")
            video_dir = os.path.join(self.base_dir, base_name)
            with open(os.path.join(video_dir, 'captions.json')) as f:
                captions = json.load(f)
            caps = list(captions.values())
            caption_emb = encode_sentences(
                sentence_list=caps,
                model_name=model,
                model_dir=self.model_dir,
            )
            print(caption_emb)
            with open(os.path.join(video_dir, f'segment_textual_embedding.pkl'), 'wb') as f:
                pickle.dump(caption_emb, f)
            end_time = time.time()
            print(f"textual encoding time for video {base_name}: {round(end_time-start_time, 3)} seconds")


    def create_visual_embedding(self):
        
        for video_path in self.video_path_list:
            base_name = os.path.basename(video_path).replace(".mp4", "")
            video_dir = os.path.join(self.base_dir, base_name)
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            
            cap = cv2.VideoCapture(video_path)
            fps = round(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = fps*self.seconds_per_feat//self.frames_per_feat
            total_feats = total_frames//(fps*self.seconds_per_feat)

            segment_feats = []
            start_time = time.time()
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for segment_id in range(total_feats):
                frames = []
                for i in range(self.frames_per_feat):
                    success, frame = cap.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame)
                    for j in range(frame_interval-1): #skip other frames
                        success, frame = cap.read()
                for i in range(fps*self.seconds_per_feat-frame_interval*self.frames_per_feat):
                    success, frame = cap.read() #skip remaining frames
                frames_tensor = frames2tensor(frames, device='cuda')
                with torch.no_grad():
                    vid_feat = get_vid_feat(frames_tensor, self.clip).cpu()
                segment_feats.append(vid_feat)
            segment_feats = torch.cat(segment_feats, dim=0).numpy()
            end_time = time.time()
            cap.release()
            print(segment_feats)
            print(f"visual embedding time for video {base_name}: {round(end_time-start_time, 3)} seconds")
            with open(os.path.join(video_dir, 'segment_visual_embedding.pkl'), 'wb') as f:
                pickle.dump(segment_feats, f)


    def run(self):
        self.create_textual_embedding()
        self.create_visual_embedding()
