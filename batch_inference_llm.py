from openai import OpenAI
from experiments.api_keys import openai_key
from enums import InferenceOptions
import json

CLIENT = OpenAI(api_key=openai_key)


def get_body(inference_option: InferenceOptions, prompt: str, dev_message: str):
    if inference_option.value == InferenceOptions.SQL_UNI.value:
        body = {
            "model": inference_option.value,
            "input": [
                {"role": "developer", "content": dev_message},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_output_tokens": 256,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "pred_sql",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "sql_query": {
                                "type": "string",
                            },
                        },
                        "required": ["sql_query"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
        }
    elif inference_option.value == InferenceOptions.SQL_REASON.value:
        body = {
            "model": inference_option.value,
            "reasoning": {"effort": "medium"},
            "input": [
                {"role": "developer", "content": dev_message},
                {"role": "user", "content": prompt},
            ],
            "max_output_tokens": 1024,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "pred_sql",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "sql_query": {
                                "type": "string",
                            },
                        },
                        "required": ["sql_query"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            },
        }

    return body


def create_batch_file(
    inference_option: InferenceOptions,
    prompts: list[str],
    dev_message: str,
    file_name: str,
):
    with open(f"./pipeline_results/{file_name}.jsonl", "wb") as f:
        for i, prompt in enumerate(prompts):
            body = get_body(inference_option, prompt, dev_message)
            req = {
                "custom_id": str(i),
                "method": "POST",
                "url": "/v1/responses",
                "body": body,
            }
            f.write(json.dumps(req).encode("utf-8"))
            f.write(b"\n")
    print(
        f"Batch file '{file_name}.jsonl'created successfully. {len(prompts)} requests."
    )


def push_batch_file(file_name: str):
    batch_input_file = CLIENT.files.create(
        file=open(f"./pipeline_results/{file_name}.jsonl", "rb"), purpose="batch"
    )
    print(batch_input_file)
    return batch_input_file.id


def create_batch(file_id, description: str):
    batch = CLIENT.batches.create(
        input_file_id=file_id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={
            "description": description,
        },
    )
    return batch


def get_batch_status(batch_id: str):
    batch = CLIENT.batches.retrieve(batch_id)
    return batch


def download_batch_results(output_file_id: str, output_file: str):
    batch_content = CLIENT.files.content(output_file_id)
    batch_content.write_to_file(f"./pipeline_results/{output_file}.jsonl")
    print(f"Batch results downloaded to {output_file}")
