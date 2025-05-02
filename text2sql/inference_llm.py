from openai import OpenAI
from experiments.api_keys import openai_key
from enums import InferenceOptions
from tqdm import tqdm

CLIIENT = OpenAI(api_key=openai_key)


def get_sql_uni_llm(prompt: str, dev_message: str, model: str):

    response = CLIIENT.responses.create(
        model=model,
        input=[
            {"role": "developer", "content": dev_message},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_output_tokens=256,
        text={
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
    )

    return response


def get_sql_reason_llm(prompt: str, dev_message: str, model: str):

    response = CLIIENT.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        input=[
            {"role": "developer", "content": dev_message},
            {"role": "user", "content": prompt},
        ],
        max_output_tokens=1024,
        text={
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
    )
    return response


def infer_llm(prompts: list[str], dev_message: str, inference_option: InferenceOptions):
    """
    Infer the SQL query using the LLM based on the provided prompt and inference option.
    Args:
        prompts (list[str]): List of prompts to be used for inference.
        dev_message (str): Developer message to be included in the inference request.
        inference_option (InferenceOptions): Inference option to determine the type of LLM to use.
    Returns:
        respopse object
    """
    if inference_option.value == InferenceOptions.SQL_UNI.value:
        infer_fn = get_sql_uni_llm
    elif inference_option.value == InferenceOptions.SQL_REASON.value:
        infer_fn = get_sql_reason_llm
    else:
        raise ValueError(f"Unknown inference option: {inference_option}")

    responses = []
    for prompt in tqdm(prompts, desc="Inferring SQL queries"):
        response = infer_fn(prompt, dev_message, inference_option.value)
        responses.append(response)

    return responses
