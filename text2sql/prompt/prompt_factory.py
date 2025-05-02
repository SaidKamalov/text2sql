from text2sql.data_models import Sample
from text2sql.enums import PromptRepresentationType, ExampleSelectionType
from text2sql.prompt.prompt_templates import OAIPrompt, ReasoningPrompt
from tqdm import tqdm


class PromptFactory:
    @staticmethod
    def build_prompts(
        prompt_type: PromptRepresentationType,
        samples: list[Sample],
        k: int = 0,
        examples: list[Sample] = None,
        example_selection_type: ExampleSelectionType = None,
        schema_info_option=None,
        add_fk_info: bool = False,
        add_cv_ref: bool = False,
        op_rule=None,
    ):

        if prompt_type.value == PromptRepresentationType.OAI.value:
            build_promt_fn = OAIPrompt.build_prompt
        elif prompt_type.value == PromptRepresentationType.REASONING.value:
            build_promt_fn = ReasoningPrompt.build_prompt
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        prompts = []
        for sample in tqdm(samples, desc="Building prompts", unit="prompt"):
            prompt_message = build_promt_fn(
                sample,
                k,
                examples,
                example_selection_type,
                schema_info_option,
                add_fk_info,
                add_cv_ref,
                op_rule,
            )
            prompts.append(prompt_message)

        return prompts


if __name__ == "__main__":
    # Example usage
    prompt = PromptFactory.build_prompts(
        prompt_type=PromptRepresentationType.OAI, samples=[]
    )
    print(prompt)
