from captioning import Captioning
from segment_feature import SegmentFeature
from tracking import Tracking
from reid import ReID
import os
import shutil
import ast
import sys
import re
from io import StringIO
from pathlib import Path
from tools import ToolKit
from langchain.agents import AgentExecutor, create_react_agent, tool
from langchain_openai import ChatOpenAI
from threading import Lock
from langchain_core.exceptions import OutputParserException
from runtime_config import (
    resolve_required_directory,
    resolve_required_environment_value,
)
import time
import pickle


CACHE_FILE = Path(__file__).with_name("react_prompt_cache.pkl")
DATABASE_QUERY_PROMPT_FILE = (
    Path(__file__).with_name("prompts") / "database_query_prompt.txt"
)


class SandboxManager:


    def __init__(self, base_dir, show_tracking=False, tracking_fps=15, sample_num=5):
        self.video_dir = resolve_required_directory("EGOSCHEMA_VIDEO_DIR")
        self.provider_api_key = resolve_required_environment_value(
            "STEPCODE_API_KEY"
        )
        self.provider_base_url = os.environ.get(
            "STEPCODE_BASE_URL",
            "https://models-proxy.stepfun-inc.com",
        ).rstrip("/")
        self.preprocessed_dir = resolve_required_directory(
            "EGOSCHEMA_CACHE_DIR"
        )
        self.videollava_runtime_dir = resolve_required_directory(
            "VIDEO_LLAVA_RUNTIME_DIR"
        )
        self.model_dir = resolve_required_directory(
            "VIDEO_AGENT_MODEL_DIR"
        )
        self.base_dir = base_dir
        self.show_tracking = show_tracking
        self.tracking_fps = tracking_fps
        self.sample_num = sample_num

        # Initialize processing components
        self.captioning = Captioning(
            video_path_list=[],
            base_dir=self.base_dir,
            model_dir=self.model_dir,
        )
        self.temporal_feature = SegmentFeature(
            video_path_list=[],
            base_dir=self.base_dir,
            model_dir=self.model_dir,
        )
        self.tracking = Tracking(
            video_path_list=[],
            base_dir=self.base_dir,
            model_dir=self.model_dir,
            tracking_fps=self.tracking_fps,
            sample_num=self.sample_num,
            show=self.show_tracking
        )
        self.reid = ReID(video_path_list=[], base_dir=self.base_dir)
        self.preprocess_resource_lock = Lock()
        self.llava_lock = Lock()
        self.datastructures_lock = Lock()

        self.loaded_video = {}
        self.fork_count = {}
        self.toolkits = {}
        self.completed_stop_operations = {}


    def create_sandbox(self, sandbox_id):
        """Create a sandbox directory for video processing."""
        sandbox_path = os.path.join(self.base_dir, sandbox_id)
        os.makedirs(sandbox_path, exist_ok=False)
        return sandbox_path
    
    def fork(self, sandbox_id):
        
        with self.datastructures_lock:
            sandbox_path = os.path.join(self.base_dir, sandbox_id)

            if not os.path.exists(sandbox_path):
                raise FileNotFoundError(f"Sandbox {sandbox_id} not found")

            st = time.perf_counter()
            if sandbox_id not in self.fork_count:
                self.fork_count[sandbox_id] = 0
            
            self.fork_count[sandbox_id] += 1

            forked_sandbox_id = f'{sandbox_id}_{self.fork_count[sandbox_id]}'
            forked_sandbox_path = os.path.join(self.base_dir, forked_sandbox_id)

            previous_fork_count = self.fork_count[sandbox_id] - 1
            try:
                shutil.copytree(sandbox_path, forked_sandbox_path)
            except BaseException as primary_error:
                cleanup_errors = []
                if os.path.exists(forked_sandbox_path):
                    try:
                        shutil.rmtree(forked_sandbox_path)
                    except BaseException as cleanup_error:
                        cleanup_errors.append(cleanup_error)

                if not cleanup_errors:
                    if previous_fork_count == 0:
                        self.fork_count.pop(sandbox_id, None)
                    else:
                        self.fork_count[sandbox_id] = previous_fork_count

                if cleanup_errors:
                    raise RuntimeError(
                        f"{primary_error} and partial fork rollback failed: "
                        f"{cleanup_errors[0]}"
                    ) from primary_error
                raise
            et = time.perf_counter()
            print(f'Time taken to fork: {sandbox_id} to {forked_sandbox_path} is {et - st}')
            if sandbox_id in self.loaded_video:
                self.loaded_video[forked_sandbox_id] = self.loaded_video[sandbox_id]
            source_has_toolkit = sandbox_id in self.toolkits
        
        if source_has_toolkit:
            try:
                self.generate_toolkit(sandbox_id=forked_sandbox_id)
            except BaseException as primary_error:
                try:
                    self.stop_sandbox(
                        forked_sandbox_id,
                        operation_id=(
                            f"fork-toolkit-cleanup:{forked_sandbox_id}"
                        ),
                    )
                except BaseException as cleanup_error:
                    raise RuntimeError(
                        "fork toolkit creation failed and copied sandbox "
                        "cleanup also failed"
                    ) from primary_error
                raise

        return {"sandbox_id": forked_sandbox_id}


    def load_video_into_sandbox(self, video_name, sandbox_id):
        """Copy a video from sample_videos into the sandbox."""
        with self.datastructures_lock:
            source_path = os.path.join(self.video_dir, video_name)
            self.loaded_video[sandbox_id] = video_name
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Video {video_name} not found in {source_path} directory")

            # destination follows the structure: base_dir/sandbox_id/video.mp4
            dest_dir = os.path.join(self.base_dir, sandbox_id)
            dest_path = os.path.join(dest_dir, "video.mp4")
            shutil.copy2(source_path, dest_path)

            return 'Successfully loaded video into the sandbox'


    def stop_sandbox(self, sandbox_id, operation_id):
        """Stop and remove a sandbox directory."""
        if not isinstance(sandbox_id, str) or not sandbox_id:
            raise ValueError("sandbox_id must be a non-empty string")
        if not isinstance(operation_id, str) or not operation_id:
            raise ValueError("operation_id must be a non-empty string")

        with self.datastructures_lock:
            if operation_id in self.completed_stop_operations:
                completed_sandbox_id = self.completed_stop_operations[
                    operation_id
                ]
                if completed_sandbox_id != sandbox_id:
                    raise RuntimeError(
                        f"Stop operation '{operation_id}' already belongs "
                        f"to sandbox '{completed_sandbox_id}'"
                    )
                return True

            print(f'DELETING AND REMOVING SANDBOX: {sandbox_id}')
            sandbox_path = os.path.join(self.base_dir, sandbox_id)
            if not os.path.exists(sandbox_path):
                raise FileNotFoundError(f"Sandbox {sandbox_id} not found")

            if sandbox_id in self.toolkits:
                self.toolkits[sandbox_id].cleanup()
                del self.toolkits[sandbox_id]
            
            self.fork_count.pop(sandbox_id, None)

            shutil.rmtree(sandbox_path)
            self.loaded_video.pop(sandbox_id, None)
            self.completed_stop_operations[operation_id] = sandbox_id

            return True


    def sandbox_exists(self, sandbox_id):
        """Check if a sandbox exists."""
        sandbox_path = os.path.join(self.base_dir, sandbox_id)
        return os.path.exists(sandbox_path)

    def generate_toolkit(self, sandbox_id):
        base_dir = os.path.join(self.base_dir, sandbox_id)
        toolkit = ToolKit(
            video_path=os.path.join(base_dir, "video.mp4"),
            base_dir=base_dir,
            vqa_tool='videollava',
            use_reid=True,
            captioning=self.captioning,
            videollava_runtime_dir=self.videollava_runtime_dir,
            model_dir=self.model_dir,
        )

        with self.datastructures_lock:
            self.toolkits[sandbox_id] = toolkit

    def preprocess(self, sandbox_id):
        """Preprocess video in the sandbox by building temporal and object memory."""

        # Acquire lock
        with self.preprocess_resource_lock:
            print(f'Acquired lock to preprocess {sandbox_id}')

            base_dir = os.path.join(self.base_dir, sandbox_id)
            video_path_list = [os.path.join(base_dir, "video.mp4")]

            # Directory containing preprocessed video folders (configurable)
            preprocessed_dir = self.preprocessed_dir

            def check_has_been_preprocessed(video_path):
                """Check if all required preprocessing files exist."""
                base_name = os.path.basename(video_path).replace(".mp4", "")
                video_dir = os.path.join(base_dir, base_name)
                if not os.path.exists(video_dir):
                    return False
                files = os.listdir(video_dir)
                required_files = [
                    "captions.json",
                    "segment_textual_embedding.pkl",
                    "segment_visual_embedding.pkl",
                    "segment2id.json",
                    "tracking.pkl",
                    "reid.pkl",
                    "tid2clip.pkl",
                    "tid2dinov2.pkl",
                    "uid2clip.pkl",
                    "reid.mp4"
                ]
                for f in required_files:
                    if f not in files:
                        return False
                return True

            def copy_preprocessed_data(video_path):
                """Check if preprocessed data exists in preprocessed_dir and copy it."""
                base_name = os.path.basename(video_path).replace(".mp4", "")
                video_dir = os.path.join(base_dir, base_name)

                # Check if preprocessed directory exists and contains the video folder
                if os.path.exists(preprocessed_dir) and sandbox_id in self.loaded_video:
                    
                    preprocessed_video_dir = os.path.join(preprocessed_dir, self.loaded_video[sandbox_id].replace('.mp4', ''), 'video')

                    if os.path.exists(preprocessed_video_dir) and os.path.isdir(preprocessed_video_dir):
                        print(f'Found preprocessed data in {preprocessed_video_dir}, copying to {sandbox_id}')

                        # Create destination directory if it doesn't exist
                        os.makedirs(video_dir, exist_ok=True)

                        # Copy all files from the preprocessed video folder
                        st = time.perf_counter()
                        for item in os.listdir(preprocessed_video_dir):
                            src = os.path.join(preprocessed_video_dir, item)
                            dst = os.path.join(video_dir, item)
                            if os.path.isfile(src):
                                shutil.copy2(src, dst)
                            elif os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                        et = time.perf_counter()
                        print(f'Successfully copied preprocessed data from {preprocessed_dir}/{base_name} in {et - st}')
                        return True
                return False

            for video_path in video_path_list:
                if not check_has_been_preprocessed(video_path):
                    copy_preprocessed_data(video_path)

            preprocess_list = []
            for video_path in video_path_list:
                if not check_has_been_preprocessed(video_path):
                    preprocess_list.append(video_path)
                else:
                    self.generate_toolkit(sandbox_id=sandbox_id)

            if len(preprocess_list) == 0:
                return

            self.captioning.video_path_list = preprocess_list
            self.captioning.base_dir = base_dir
            self.captioning.run()

            self.temporal_feature.video_path_list = preprocess_list
            self.temporal_feature.base_dir = base_dir
            self.temporal_feature.run()

            # build object memory
            self.tracking.video_path_list = preprocess_list
            self.tracking.base_dir = base_dir
            self.tracking.run()

            self.reid.video_path_list = preprocess_list
            self.reid.base_dir = base_dir
            self.reid.run()

            self.generate_toolkit(sandbox_id=sandbox_id)

    def get_toolkit(self, sandbox_id):
        with self.datastructures_lock:
            return self.toolkits[sandbox_id]

    def object_memory_querying(self, sandbox_id, question):
        """Given a question about open-vocabulary objects such as 'how many people are there in the video?' or 'In which segments did the brown dog appear?', this tool will give the answer based on the object memory."""
        
        toolkit = self.get_toolkit(sandbox_id)

        @tool
        def database_querying(program):
            """given a MySQL program, this tool will query the database and return the results."""
            ans = toolkit.query_database(program=program)
            return '\n'+ans+'\n'
        @tool
        def open_vocabulary_object_retrieval(description):
            """given an open-vocabulary description of an object or a person (frying pan, person in red clothes e.g.), this tool will return the possible candidate object IDs that satisfy the description."""
            ans = toolkit.retrieve_candidate_objects(description=description)
            return '\n'+ans+'\n'
        
        with CACHE_FILE.open('rb') as f:
            prompt = pickle.load(f)
        
        with DATABASE_QUERY_PROMPT_FILE.open() as f:
            t = f.read()
        
        prompt.template = t

        provider_api_key = getattr(self, "provider_api_key", "")
        provider_base_url = getattr(
            self,
            "provider_base_url",
            "https://models-proxy.stepfun-inc.com",
        ).rstrip("/")
        if not provider_base_url.endswith("/v1"):
            provider_base_url += "/v1"
        llm = ChatOpenAI(
            model="deepseek-v4-flash",
            temperature=0.0,
            api_key=provider_api_key,
            base_url=provider_base_url,
            model_kwargs={
                "extra_body": {"thinking": {"type": "disabled"}},
            },
        )
        tools = [database_querying, open_vocabulary_object_retrieval]
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            # A provider may return a natural-language terminal answer after
            # querying the object memory. Preserve that answer as tool output
            # so the outer local rollout can continue and record the call.
            handle_parsing_errors=True,
        )

        # original_stdout = sys.stdout
        # output_catcher = StringIO()
        # sys.stdout = output_catcher

        output = agent_executor.invoke({"input": question})
        return output['output']


    def segment_localization(self, sandbox_id, description):
        """Given a textual description, this tool will return the top-5 candidate segments that are most relevant to the description."""
        toolkit = self.get_toolkit(sandbox_id)
        answer = toolkit.segment_localization(description, k=5)
        return '\n'+answer+'\n'

    def log(self, line):
        with open('sandbox.log', 'a') as log_file:
            log_file.write(line)
            log_file.write('\n')

    def caption_retrieval(self, sandbox_id, input_tuple):
        """given an input tuple (start_segment_ID, end_segment_ID), this tool will retrieve all the captions between the two segments, 15 captions at most. end_segment_ID < start_segment_ID + 15."""
        
        input_tuple = ast.literal_eval(input_tuple)
        toolkit = self.get_toolkit(sandbox_id)
        if len(input_tuple) != 2:
            return "\nInvalid input tuple!\n"
        answer = toolkit.caption_retrieval(int(input_tuple[0]), int(input_tuple[1]))
        return '\n'+answer+'\n'


    def visual_question_answering(self, sandbox_id, input_tuple):
        """Given an input tuple (question, segment_ID), this tool will focus on the video segments starting from segment_ID-1 to segment_ID+1. It will return the description of the video segment and the answer to the question based on the segment."""

        with self.llava_lock:
            input_tuple = ast.literal_eval(input_tuple)
            toolkit = self.get_toolkit(sandbox_id)
            if len(input_tuple) != 2:
                return "\nInvalid input tuple!\n"
            question = input_tuple[0]
            segment_id = int(input_tuple[1])
            print(f'Visual question answering on {question} and segment {segment_id}')
            answer = toolkit.visual_question_answering(question, segment_id)

        return '\n'+answer+'\n'

# Need thread safety only for preprocess and llava access
