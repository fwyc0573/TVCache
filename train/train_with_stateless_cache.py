import logging
import asyncio
import os
import time
from tool_schema import Response
import chz
import datasets
import tinker
import torch
from tinker import types
from tinker.types.tensor_data import TensorData
from tinker_cookbook import checkpoint_utils, model_info, renderers
from tinker_cookbook.rl.data_processing import trajectory_to_data
from tinker_cookbook.tokenizer_utils import get_tokenizer
from tinker_cookbook.utils import ml_log
import json
from cached_agent_loop import CachedVideoAgentLoop, SharedToolCache
from utils.dataset_selection import select_dataset_slice
from utils.rollout_execution import run_agent_loops
from utils.rollout_metrics import build_rollout_record, write_rollout_records
from utils.training_update import apply_training_update
import random

from typing import List, Dict

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARN)
random.seed(8)

@chz.chz
class Config:
    base_url: str | None = None
    log_path: str = "./tests/rebuttal"
    model_name: str = "Qwen/Qwen3.6-35B-A3B"
    renderer_name: str = "qwen3_disable_thinking"
    batch_size: int = 4
    group_size: int = 8
    learning_rate: float = 4e-5
    max_length: int = 32768
    lora_rank: int = 32
    save_every: int = 5
    max_tokens: int = 1024
    num_turns: int = 5
    sandbox_base_url: str = "http://localhost:5000"
    dataset_start: int = 0
    dataset_count: int = 100
    epochs: int = 10


def get_reward(response: str, answer: str) -> float:
    return 0.0

def get_prompt(question: str, options: Dict[str, str], video_id: str) -> str:
    with open('./prompt.txt', 'r') as prompt_file:
        prompt_template = prompt_file.read()

        # Format the question with options
        formatted_question = question + "\n\nOptions:\n"
        for key in sorted(options.keys()):
            formatted_question += f"{key}: {options[key]}\n"

        prompt = prompt_template.replace('{QUESTION}', formatted_question)
        prompt += f'\nThe associated video name is {video_id}.mp4.'
        prompt = prompt.replace('{response_schema}', json.dumps(Response.model_json_schema(), indent='\t'))
        return prompt

def get_video_dataset(dataset_start: int, dataset_count: int) -> List[dict]:
    json_path = './EgoSchema/processed_videos.json'

    dataset = []

    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        for dataset_index, point in enumerate(data):
            question_prompt = get_prompt(point['question'], point['options'], point['video_id'])
            dataset.append(
                {
                    "question": question_prompt,
                    "answer": point["correct_answer_index"],
                    "dataset_index": dataset_index,
                    "video_id": point["video_id"],
                }
            )
    
    return select_dataset_slice(dataset, dataset_start, dataset_count)

def get_task_id(question: str) -> str:
    lines = question.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('The associated video name is'):
            parts = line.split()
            return parts[-1]


async def main(config: Config):
    rollout_log_dir = os.path.join(config.log_path, "rollouts")
    run_id = f"stateless_cache_{time.time_ns()}"

    # Setup logging
    ml_logger = ml_log.setup_logging(
        log_dir=config.log_path,
        wandb_project=None,
        wandb_name=None,
        config=config,
        do_configure_logging_module=True,
    )

    # Get tokenizer and renderer
    tokenizer = get_tokenizer(config.model_name)
    renderer = renderers.get_renderer(config.renderer_name, tokenizer)
    logger.info(f"Using renderer: {config.renderer_name}")

    # Load GSM8K dataset
    logger.info("Loading dataset...")
    dataset = get_video_dataset(config.dataset_start, config.dataset_count)

    
    train_dataset = []
    for _ in range(config.epochs):
        random.shuffle(dataset)
        train_dataset.extend(dataset)
        
    n_train_batches = len(train_dataset) // config.batch_size

    # Setup training client
    service_client = tinker.ServiceClient(base_url=config.base_url)

    resume_info = checkpoint_utils.get_last_checkpoint(config.log_path)
    if resume_info:
        training_client = await service_client.create_training_client_from_state_async(
            resume_info["state_path"]
        )
        start_batch = resume_info["batch"]
        logger.info(f"Resuming from batch {start_batch}")
    else:
        training_client = await service_client.create_lora_training_client_async(
            base_model=config.model_name, rank=config.lora_rank
        )
        start_batch = 0

    sampling_params = tinker.types.SamplingParams(
        max_tokens=config.max_tokens,
        stop=renderer.get_stop_sequences(),
    )
    # Optimizer step
    adam_params = types.AdamParams(
        learning_rate=config.learning_rate, beta1=0.9, beta2=0.95, eps=1e-8
    )

    logger.info(f"Training for {n_train_batches} batches")

    #  Main training loop
    batch_idx = start_batch
    next_batch_idx = batch_idx + 1

    while batch_idx < n_train_batches:
        # Setup metrics for logging
        t_start = time.time()
        step = batch_idx
        metrics: dict[str, float] = {
            "progress/batch": batch_idx,
            "optim/lr": config.learning_rate,
            "progress/done_frac": (batch_idx + 1) / n_train_batches,
        }

        # Save checkpoint
        if step % config.save_every == 0 and step > 0:
            await checkpoint_utils.save_checkpoint_async(
                training_client=training_client,
                name=f"{step:06d}",
                log_path=config.log_path,
                kind="state",
                loop_state={"batch": batch_idx},
            )

        # Get training batch and convert to datums online
        batch_start = batch_idx * config.batch_size
        batch_end = min((batch_idx + 1) * config.batch_size, len(train_dataset))
        batch_rows = train_dataset[batch_start: batch_end]

        sampling_path_future = await training_client.save_weights_for_sampler_async(name=f"{step:06d}")
        sampling_path = await sampling_path_future
        sampling_client = await service_client.create_sampling_client_async(model_path=sampling_path.path)

        training_datums: list[types.Datum] = []
        batch_rewards: list[float] = []
        batch_reward_lists: List[List[float]] = []
        batch_rollout_elapsed_seconds: list[float] = []

        rollout_groups: List[List[CachedVideoAgentLoop]] = []
        sandbox_ids: List[str] = []
        shared_cache = SharedToolCache()

        if next_batch_idx < n_train_batches:
            next_batch_start = next_batch_idx * config.batch_size
            next_batch_end = min((next_batch_idx + 1) * config.batch_size, len(train_dataset))
            next_batch_data = train_dataset[next_batch_start: next_batch_end]

            next_batch_task_ids = [get_task_id(nd['question']) for nd in next_batch_data]
            

        for d_idx, data in enumerate(batch_rows):
            agent_loops: List[CachedVideoAgentLoop] = []

            for i in range(config.group_size):

                agent_loop = CachedVideoAgentLoop(
                    training_data_point=data,
                    sampling_client=sampling_client,
                    num_turns=config.num_turns,
                    renderer=renderer,
                    shared_cache=shared_cache,
                    sandbox_base_url=config.sandbox_base_url,
                    rollout_log_dir=rollout_log_dir,
                )

                # Start sandbox with unique ID
                sandbox_id = f"{run_id}_batch_{batch_idx}_data_{batch_rows.index(data)}_rollout_{i}"
                agent_loops.append(agent_loop)
                sandbox_ids.append(sandbox_id)
            
            rollout_groups.append(agent_loops)
        
        flat_agent_loops = [
            agent_loop
            for agent_loop_list in rollout_groups
            for agent_loop in agent_loop_list
        ]
        results = await run_agent_loops(
            flat_agent_loops,
            sandbox_ids,
            sampling_params=sampling_params,
        )
        result_index = 0

        batch_agent_results = []
        batch_rollout_records = []

        for data_idx, data in enumerate(batch_rows):
            data_agent_loops = rollout_groups[data_idx]
            data_agent_loop_results = []

            for rollout_index in range(config.group_size):
                agent_loop = data_agent_loops[rollout_index]
                rollout_result = results[result_index]
                sandbox_id = sandbox_ids[result_index]
                data_agent_loop_results.append(rollout_result)
                batch_rollout_records.append(
                    build_rollout_record(
                        variant="stateless_cache",
                        batch_index=batch_idx,
                        dataset_index=data["dataset_index"],
                        rollout_index=rollout_index,
                        sandbox_id=sandbox_id,
                        video_id=data["video_id"],
                        agent_loop=agent_loop,
                        execution_result=rollout_result,
                    )
                )
                result_index += 1

            assert len(data_agent_loops) == len(data_agent_loop_results)
            
            batch_agent_results.append(
                {
                    'data': data,
                    'agent_loops': data_agent_loops,
                    'results': data_agent_loop_results
                }
            )
        write_rollout_records(config.log_path, batch_rollout_records)
        
        # Process each group of rollouts
        for item in batch_agent_results:
            data = item['data']
            agent_loops = item['agent_loops'] # rollouts
            rollout_results = item['results']

            group_rewards: list[float] = []
            group_trajectories = []

            for agent_loop, rollout_result in zip(agent_loops, rollout_results):
                trajectory = rollout_result.output
                batch_rollout_elapsed_seconds.append(
                    rollout_result.elapsed_seconds
                )

                group_trajectories.append(trajectory)

                reward = agent_loop.get_reward()
                group_rewards.append(reward)
            

            mean_reward = sum(group_rewards) / len(group_rewards)
            advantages = [reward - mean_reward for reward in group_rewards]
            batch_rewards.append(mean_reward)
            batch_reward_lists.append(group_rewards)

            # Skip if all advantages are zero
            if all(advantage == 0.0 for advantage in advantages):
                continue

            for trajectory, advantage in zip(
                group_trajectories,
                advantages,
            ):
                training_datums.extend(
                    trajectory_to_data(trajectory, advantage)
                )

        await apply_training_update(
            training_client=training_client,
            training_datums=training_datums,
            adam_params=adam_params,
            metrics=metrics,
        )

        # Log metrics[]
        metrics["time/total"] = time.time() - t_start
        metrics["reward/average"] = sum(batch_rewards) / len(batch_rewards)
        metrics["reward/list"] = batch_reward_lists 
        metrics["rollout/elapsed_seconds_total"] = sum(
            batch_rollout_elapsed_seconds
        )
        metrics["rollout/elapsed_seconds_average"] = sum(
            batch_rollout_elapsed_seconds
        ) / len(batch_rollout_elapsed_seconds)
        ml_logger.log_metrics(metrics, step=batch_idx)

        batch_idx = next_batch_idx
        next_batch_idx += 1

    await checkpoint_utils.save_checkpoint_async(
        training_client=training_client,
        name="final",
        log_path=config.log_path,
        kind="both",
        loop_state={"batch": n_train_batches},
    )
    ml_logger.close()
    logger.info("Training completed")


if __name__ == "__main__":
    asyncio.run(chz.nested_entrypoint(main))
