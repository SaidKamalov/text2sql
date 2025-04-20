import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from data_models import Sample


def select_k_shot_examples(
    target_sample: Sample, k: int, possible_examples: list[Sample]
) -> list:
    # TODO:
    # - change file_path to samples
    """
    Select k most similar examples to the given sample from the file, based on cosine similarity of questions using sentence embeddings.
    Args:
        sample: Sample object with a 'question' attribute.
        k: number of examples to select.
        file_path: path to the json file with examples (should have 'question' field).
    Returns:
        List of k most similar example dicts.
    """

    # Extract all questions
    questions = [ex.question for ex in possible_examples]
    # Add the input sample's question at the end
    all_questions = questions + [target_sample.question]

    # Load sentence transformer model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(all_questions)

    # Compute cosine similarity between sample and all examples
    sim_scores = cosine_similarity([embeddings[-1]], embeddings[:-1]).flatten()

    # Get indices of top-k most similar examples
    top_k_idx = sim_scores.argsort()[-k:][::-1]

    # Return the corresponding examples
    return [possible_examples[i] for i in top_k_idx]


if __name__ == "__main__":
    pass
