"""Probe JSON generation after replaying observed local video tool outputs."""

import argparse
import json
import os
from pathlib import Path
import time

import httpx
from tool_schema import Response

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--tool-choice-none', action='store_true')
parser.add_argument('--history', type=Path)
parser.add_argument('--json-arguments', action='store_true')
parser.add_argument('--disable-thinking', action='store_true')
parser.add_argument('--native-response', action='store_true')
parser.add_argument('--text-history', action='store_true')
parser.add_argument('--native-tools', action='store_true')
args = parser.parse_args()
repo = Path(__file__).resolve().parents[2]
task = repo / 'task_memory/task_2026-08-14_tvcache_rl_rollout_reproduction'
manifest = json.loads((task / 'egoschema_manifest_2026-09-08.json').read_text())
smoke = json.loads((task / 'tvcache-real-rollout-h200-20260910-b-tool-smoke.json').read_text())
question = manifest['question'] + '\n\nOptions:\n' + '\n'.join(
    f'{i}: {option}' for i, option in enumerate(manifest['options']))
prompt = (repo / 'train/prompt.txt').read_text().replace('{QUESTION}', question).replace(
    '{response_schema}', json.dumps(Response.model_json_schema()))
prompt += f'\nThe associated video name is {manifest["video_id"]}.mp4.'
messages = [{'role': 'user', 'content': prompt}]
inputs = {
    'load_video_into_sandbox': manifest['video_id'] + '.mp4',
    'preprocess': '', 'caption_retrieval': '(0, 1)',
    'segment_localization': 'a person painting a picture',
}
for row in smoke['calls']:
    tool = row['command']
    if tool not in inputs:
        continue
    call_id = f'probe-{tool}'
    action = {'tool': tool, 'inputs': inputs[tool]}
    messages.append({'role': 'assistant', 'content': json.dumps({
        'thought': 'Gather evidence from the video.', 'actions': [action], 'final_answer': None}),
        'tool_calls': [{'id': call_id, 'type': 'function', 'function': {
            'name': tool, 'arguments': inputs[tool]}}]})
    messages.append({'role': 'tool', 'name': tool, 'tool_call_id': call_id,
                     'content': row['body']['result']})
if args.history:
    messages = json.loads(args.history.read_text().splitlines()[-1])['messages']
if args.json_arguments:
    for message in messages:
        for call in message.get('tool_calls', []):
            call['function']['arguments'] = json.dumps({'inputs': call['function']['arguments']})
if args.text_history:
    messages = [
        {'role': 'user', 'content': json.dumps({'tool': m['name'], 'result': m['content']})}
        if m['role'] == 'tool' else {'role': m['role'], 'content': m['content']}
        for m in messages
    ]
payload = {'model': 'deepseek-v4-flash', 'messages': messages,
           'response_format': {'type': 'json_object'}}
if args.tool_choice_none:
    payload['tool_choice'] = 'none'
if args.disable_thinking:
    payload['thinking'] = {'type': 'disabled'}
if args.native_response:
    payload.pop('response_format')
    payload['tools'] = [{'type': 'function', 'function': {
        'name': 'agent_response', 'description': 'Return the next locally executed actions or final answer.',
        'parameters': Response.model_json_schema()}}]
    payload['tool_choice'] = {'type': 'function', 'function': {'name': 'agent_response'}}
native_names = ['load_video_into_sandbox', 'preprocess', 'object_memory_querying',
                'segment_localization', 'caption_retrieval', 'visual_question_answering']
if args.native_tools:
    payload.pop('response_format')
    messages[0]['content'] = messages[0]['content'].split('Your response must be a JSON object')[0]
    messages[0]['content'] += '\nUse native function calls for local tools. Use submit_answer when ready.'
    payload['tools'] = [{'type': 'function', 'function': {'name': name,
        'description': f'Execute the local {name} tool described in the task instruction.',
        'parameters': {'type': 'object', 'properties': {'inputs': {'type': 'string'}},
                       'required': ['inputs'], 'additionalProperties': False}}} for name in native_names]
    payload['tools'].append({'type': 'function', 'function': {'name': 'submit_answer',
        'description': 'Submit the final answer.', 'parameters': {
            'type': 'object', 'properties': {'answer': {'type': 'integer', 'minimum': 0, 'maximum': 4}},
            'required': ['answer'], 'additionalProperties': False}}})
key = json.loads(Path('/data/ycfeng/home_offload/i-fengyicheng/.stepcode/config.json').read_text())['apiKey']
started = time.monotonic()
with httpx.Client(timeout=120) as client:
    response = client.post('https://models-proxy.stepfun-inc.com/v1/chat/completions',
                           headers={'Authorization': f'Bearer {key}'}, json=payload)
record = {'kind': 'protocol_replay_not_rollout', 'request': payload,
          'status_code': response.status_code, 'seconds': time.monotonic() - started,
          'response': response.json()}
args.output.write_text(json.dumps(record, indent=2) + '\n')
response.raise_for_status()
message = record['response']['choices'][0]['message']
if args.native_tools:
    calls = message['tool_calls']
    assert calls, message
    for call in calls:
        name = call['function']['name']
        arguments = json.loads(call['function']['arguments'])
        assert name in native_names + ['submit_answer'], call
        assert isinstance(arguments.get('inputs'), str) if name in native_names else arguments['answer'] in range(5)
    content = json.dumps({'thought': 'Protocol probe', 'actions': [], 'final_answer': None})
elif args.native_response:
    calls = message['tool_calls']
    assert len(calls) == 1 and calls[0]['function']['name'] == 'agent_response', calls
    content = calls[0]['function']['arguments']
else:
    content = message['content']
Response.model_validate_json(content)
print(json.dumps({'status': 'PASS', 'seconds': record['seconds'],
                  'usage': record['response']['usage'], 'tool_choice_none': args.tool_choice_none}))
