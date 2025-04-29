import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random
from data_models import Sample
from enums import ExampleSelectionType
from utils import HardnessEvaluator
import torch
import numpy as np


def _select_k_shot_examples_question_cosine_sim(
    target_sample: Sample, k: int, possible_examples: list[Sample]
) -> list:
    """
    Select k most similar examples to the given sample from set of samples, based on cosine similarity of questions using sentence embeddings.
    Args:
        target_sample: Sample object with a 'question' attribute.
        k: number of examples to select.
        possible_examples: list of Sample objects with 'question' attributes.
    Returns:
        List of k Sample objects with most similar question.
    """

    # Compute cosine similarity between sample and all examples
    sim_scores = cosine_similarity(
        np.array(target_sample.question_embedding).reshape(1, -1),
        [ex.question_embedding for ex in possible_examples],
    ).flatten()

    # Get indices of top-k most similar examples
    top_k_idx = sim_scores.argsort()[-k:][::-1]

    # Return the corresponding examples
    return [possible_examples[i] for i in top_k_idx]


def _select_k_random_examples(k: int, possible_examples: list[Sample]) -> list:
    """
    Select k random examples from the possible examples.
    Args:
        k: number of examples to select.
        possible_examples: list of Sample objects with 'question' attributes.
    Returns:
        List of k randomly selected Sample objects.
    """
    return random.sample(possible_examples, k)


def _select_k_random_examples_by_hardness(
    target_sample: Sample, k: int, possible_examples: list[Sample]
) -> list:
    """
    Select k random examples from the possible examples with same hardness.
    About hardness: https://github.com/taoyds/spider/blob/master/evaluation.py#L303
    Args:
        target_sample: Sample object with a 'question' attribute.
        k: number of examples to select.
        possible_examples: list of Sample objects with 'question' attributes.
    Returns:
        List of k randomly selected Sample objects with same hardness of the sql.
    """

    target_sample_hardness = HardnessEvaluator.eval_sql_hardness(
        target_sample.sql_parsed
    )
    # Filter examples by hardness
    sample_by_hardness = [
        ex
        for ex in possible_examples
        if HardnessEvaluator.eval_sql_hardness(ex.sql_parsed) == target_sample_hardness
    ]

    return random.sample(sample_by_hardness, k)


def _select_k_shot_examples_question_cosine_sim_same_hardness(
    target_sample: Sample, k: int, possible_examples: list[Sample]
) -> list:
    """
    Select k examples from the possible examples with same hardness, based on cosine similarity of questions using sentence embeddings.
    Args:
        target_sample: Sample object with a 'question' attribute.
        k: number of examples to select.
        possible_examples: list of Sample objects with 'question' attributes.
    Returns:
        List of k Sample objects with most similar question and same hardness.
    """
    target_sample_hardness = HardnessEvaluator.eval_sql_hardness(
        target_sample.sql_parsed
    )
    # Filter examples by hardness
    sample_by_hardness = [
        ex
        for ex in possible_examples
        if HardnessEvaluator.eval_sql_hardness(ex.sql_parsed) == target_sample_hardness
    ]

    result = []
    if len(sample_by_hardness) <= k:
        result = sample_by_hardness
    else:
        result = _select_k_shot_examples_question_cosine_sim(
            target_sample, k, sample_by_hardness
        )

    return result


def select_k_shot_examples(
    target_sample: Sample,
    k: int,
    possible_examples: list[Sample],
    selection_type: ExampleSelectionType,
) -> list:
    if selection_type.value == ExampleSelectionType.COSINE_SIM.value:
        return _select_k_shot_examples_question_cosine_sim(
            target_sample, k, possible_examples
        )
    elif selection_type.value == ExampleSelectionType.RANDOM.value:
        return _select_k_random_examples(k, possible_examples)
    elif selection_type.value == ExampleSelectionType.RAND_HARDNESS.value:
        return _select_k_random_examples_by_hardness(
            target_sample, k, possible_examples
        )
    elif selection_type.value == ExampleSelectionType.COSINE_SIM_HARDNESS.value:
        return _select_k_shot_examples_question_cosine_sim_same_hardness(
            target_sample, k, possible_examples
        )
    else:
        raise ValueError(f"Unknown selection type: {selection_type}")


if __name__ == "__main__":
    pass
