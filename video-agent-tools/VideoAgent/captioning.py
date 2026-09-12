import sys
from pathlib import Path

from runtime_config import resolve_video_agent_path

sys.path.insert(0, str(resolve_video_agent_path("LaViLa")))
import os
import urllib.request
from collections import OrderedDict
import numpy as np
import time
import torch
import torchvision.transforms as transforms
import torchvision.transforms._transforms_video as transforms_video
from LaViLa.lavila.data.video_transforms import Permute
from LaViLa.lavila.models import models as lavila_models
from LaViLa.lavila.models.tokenizer import MyGPT2Tokenizer
from LaViLa.eval_narrator import decode_one
import json
import cv2
from typing import Dict
from threading import Lock
import base64
from runtime_config import MODEL_CONFIG



class Captioning:
    def __init__(
        self,
        video_path_list,
        base_dir='preprocess',
        model_dir=None,
    ):
        self.video_path_list = video_path_list
        self.seconds_per_caption = 2 # a caption covers 2 seconds
        self.frames_per_caption = 4 # a caption is generated from 4 frames in the 2-second segments
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
        (self.model_dir / "LaViLa").mkdir(parents=True, exist_ok=True)
        start_time = time.time()
        print("=" * 60)
        print("CAPTIONING MODEL LOADING - DETAILED TIMING")
        print("=" * 60)

        crop_size = MODEL_CONFIG.lavila_crop_size
        self.val_transform = transforms.Compose([
            Permute([3, 0, 1, 2]),
            transforms.Resize(crop_size),
            transforms.CenterCrop(crop_size),
            transforms_video.NormalizeVideo(mean=[108.3272985, 116.7460125, 104.09373615000001], std=[68.5005327, 66.6321579, 70.32316305])
        ])

        # Step 1: Load checkpoint from disk
        t1 = time.time()
        ckpt_name = MODEL_CONFIG.lavila_checkpoint
        ckpt_path = self.model_dir / "LaViLa" / ckpt_name
        if not os.path.exists(ckpt_path):
            print('downloading model to {}'.format(ckpt_path))
            urllib.request.urlretrieve(
                'https://dl.fbaipublicfiles.com/lavila/checkpoints/narrator/{}'.format(ckpt_name),
                os.fspath(ckpt_path),
            )
        ckpt = torch.load(ckpt_path, map_location='cpu')
        t2 = time.time()
        print(f'[1/6] Loading checkpoint from disk: {round(t2-t1, 3)} seconds')

        # Step 2: Create state_dict
        state_dict = OrderedDict()
        for k, v in ckpt['state_dict'].items():
            state_dict[k.replace('module.', '')] = v
        t3 = time.time()
        print(f'[2/6] Creating state_dict: {round(t3-t2, 3)} seconds')

        # Step 3: Instantiate the model
        model_constructor = getattr(lavila_models, MODEL_CONFIG.lavila_constructor)
        self.model = model_constructor(
            text_use_cls_token=False,
            project_embed_dim=256,
            gated_xattn=True,
            random_init_gpt2=MODEL_CONFIG.lavila_random_init_dependencies,
            random_init_visual=MODEL_CONFIG.lavila_random_init_dependencies,
            timesformer_gated_xattn=False,
            freeze_lm_vclm=False,      # we use model.eval() anyway
            freeze_visual_vclm=False,  # we use model.eval() anyway
            num_frames=4,
            drop_path_rate=0.
        )
        t4 = time.time()
        print(f'[3/6] Instantiating model: {round(t4-t3, 3)} seconds')

        # Step 4: Load state_dict into model
        self.model.load_state_dict(state_dict, strict=True)
        t5 = time.time()
        print(f'[4/6] Loading state_dict into model: {round(t5-t4, 3)} seconds')

        # Step 5: Move model to CUDA
        self.model.cuda()
        t6 = time.time()
        print(f'[5/6] Moving model to CUDA: {round(t6-t5, 3)} seconds')

        # Step 6: Set model to eval mode
        self.model.eval()

        # Log model size in MB
        model_size_mb = sum(p.numel() * p.element_size() for p in self.model.parameters()) / (1024 * 1024)
        print(f'Captioning Model Size: {model_size_mb:.2f} MB')

        # Step 7: Load tokenizer
        tokenizer_path = self.model_dir / MODEL_CONFIG.lavila_tokenizer
        if not tokenizer_path.is_dir():
            raise NotADirectoryError(
                f"LaViLa tokenizer directory is required: {tokenizer_path}"
            )
        self.tokenizer = MyGPT2Tokenizer(str(tokenizer_path), add_bos=True)
        end_time = time.time()
        print(f'[6/6] Loading tokenizer: {round(end_time-t6, 3)} seconds')
        print(f'Total time for loading captioning model: {round(end_time-start_time, 3)} seconds')
        print("=" * 60)

        self.model_lock = Lock()
        self.captioning_prompt = ''
        with resolve_video_agent_path("captioning_prompt.txt").open(
            "r"
        ) as prompt_file:
            self.captioning_prompt = prompt_file.read()

    def get_captions_from_frames(self, frames: torch.Tensor) -> str:
        
        with self.model_lock:
            with torch.no_grad():
                input_frames = frames.cuda(non_blocking=True)
                image_features = self.model.encode_image(input_frames)
                generated_text_ids, ppls = self.model.generate(
                    image_features,
                    self.tokenizer,
                    target=None,  # free-form generation
                    max_text_length=77,
                    top_k=None,
                    top_p=0.95,   # nucleus sampling
                    num_return_sequences=5,  # number of candidates: 5
                    temperature=0.7,
                    early_stopping=True,
                )
            
            text = ""
            length = -1
            for i in range(5):
                # select the longest candidate as the caption
                generated_text_str = decode_one(generated_text_ids[i], self.tokenizer)
                if len(generated_text_str) > length:
                    length = len(generated_text_str)
                    text = generated_text_str  
            
            return text

    def generate_captions_for_frames(self, video_path: str, start_frame_idx: int, end_frame_idx: int) -> Dict[int, str]:
        caption_dict = {}

        seconds_per_caption = 2 # a caption covers 1
        subset_frames_per_caption = 4 # a caption is generated from 4 frames in the 2-second segments
        print(f'Video path for generation captions: {video_path}')

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Unable to open video file.")
            return
        fps = round(cap.get(cv2.CAP_PROP_FPS))
        total_frames = end_frame_idx - start_frame_idx
        
        frames_per_caption = fps * seconds_per_caption

        total_captions = total_frames // frames_per_caption
        frame_interval = np.ceil(frames_per_caption / subset_frames_per_caption)

        # print(f'FPS={fps}, SFI={start_frame_idx}, EFI={end_frame_idx}, Total={total_frames}, TOTAL_CAPTIONS={total_captions}, FRAME INTERVAL={frame_interval}')
        
        skipped = 0

        while skipped < start_frame_idx:
            _, _ = cap.read()
            skipped += 1

        
        captions_per_segment = max(1, int(round(fps * seconds_per_caption)))
        frame_interval = max(1, captions_per_segment // subset_frames_per_caption)
        for caption_start in range(0, total_frames, captions_per_segment):
            frames = []
            for offset in range(0, captions_per_segment, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_idx + caption_start + offset)
                success, frame = cap.read()
                if not success:
                    raise RuntimeError("failed to read a frame for local captioning")
                if hasattr(frame, "shape") and len(frame.shape) >= 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(torch.tensor(frame, dtype=torch.float32))
            frame_tensor = torch.stack(frames, dim=0)
            frame_tensor = self.val_transform(frame_tensor).unsqueeze(0)
            caption_dict[start_frame_idx + caption_start] = self.get_captions_from_frames(
                frame_tensor
            )

        cap.release()
        return caption_dict, 0, 0
        # for caption_id in range(total_captions):
        #     frames = []
            
        #     caption_frame_start = caption_id * frames_per_caption
        #     caption_frame_start += start_frame_idx # offset the start frame

        #     for idx in range(frames_per_caption):
        #         success, frame = cap.read()
        #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #         if idx % frame_interval == 0:
        #             print(f'adding {idx}')
        #             frames.append(frame)
                    
        #     print(f'Length of frames: {len(frames)}')

        #     frames = [torch.tensor(frame, dtype=torch.float32) for frame in frames]
        #     frames = torch.stack(frames, dim=0)
        #     frames = self.val_transform(frames)
        #     frames = frames.unsqueeze(0)

        #     print(f'Shape of frames: {frames.shape}')

        #     caption_text = self.get_captions_from_frames(frames)
        #     caption_dict[caption_frame_start] = caption_text
        
        # return caption_dict


            

    def generate_captions_for_all_videos(self):
        """create the captions for all videos"""
        
        for video_path in self.video_path_list:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print("Error: Unable to open video file.")
                continue
            fps = round(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            total_captions = total_frames//(fps*self.seconds_per_caption)
            frame_interval = fps*self.seconds_per_caption//self.frames_per_caption # the interval between two selected frames
        
            base_name = os.path.basename(video_path).replace(".mp4", "")
            video_dir = os.path.join(self.base_dir, base_name)
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)

            captions = dict()
            start_time = time.time()
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for caption_id in range(total_captions):
                frames = []
                for i in range(self.frames_per_caption): # 4 frames are selected for generating the caption
                    success, frame = cap.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame)
                    for j in range(frame_interval-1): #skip other frames
                        success, frame = cap.read()
                for i in range(fps*self.seconds_per_caption-frame_interval*self.frames_per_caption):
                    success, frame = cap.read() #skip remaining frames
                frames = [torch.tensor(frame, dtype=torch.float32) for frame in frames]
                frames = torch.stack(frames, dim=0)
                frames = self.val_transform(frames)
                frames = frames.unsqueeze(0)

                with torch.no_grad():
                    input_frames = frames.cuda(non_blocking=True)
                    image_features = self.model.encode_image(input_frames)
                    generated_text_ids, ppls = self.model.generate(
                        image_features,
                        self.tokenizer,
                        target=None,  # free-form generation
                        max_text_length=77,
                        top_k=None,
                        top_p=0.95,   # nucleus sampling
                        num_return_sequences=5,  # number of candidates: 5
                        temperature=0.7,
                        early_stopping=True,
                    )
                text = ""
                length = -1
                for i in range(5):
                    # select the longest candidate as the caption
                    generated_text_str = decode_one(generated_text_ids[i], self.tokenizer)
                    if len(generated_text_str) > length:
                        length = len(generated_text_str)
                        text = generated_text_str
                caption_start_frame = caption_id*fps*self.seconds_per_caption
                caption_end_frame = (caption_id+1)*fps*self.seconds_per_caption
                segment = "{}_{}".format(str(caption_start_frame), str(caption_end_frame))
                captions[segment] = text
                print(f"id: {caption_id}, frame_interval: {segment}, caption: {text}")
            end_time = time.time()
            cap.release()
            print(f"captioning time for video {base_name}: {round(end_time-start_time, 3)} seconds")
            with open(os.path.join(video_dir, "captions.json"), 'w') as f:
                json.dump(captions, f)
            segments = list(captions)
            segment2id = dict()
            for segment in segments:
                segment2id[segment] = len(segment2id)
            with open(os.path.join(video_dir, "segment2id.json"), 'w') as f:
                json.dump(segment2id, f)

    def run(self):
        self.generate_captions_for_all_videos()
