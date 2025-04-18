from openai import OpenAI
from experiments.api_keys import openai_key

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
