from enum import Enum


class ShemaInfoOptions(Enum):
    """
    Enum class for schema information options.
    """

    FULL_SCHEMA = "full_schema"
    LINKED_SCHEMA = "linked_schema"


class ExampleSelectionType(Enum):
    """
    Enum class for example selection types for k-shot scenarious.
    """

    COSINE_SIM = "cosine_sim"
    RANDOM = "random"
    RAND_HARDNESS = "random_hardness"
    COSINE_SIM_HARDNESS = "cosine_sim_hardness"


class PromptRepresentationType(Enum):
    """
    Enum class for prompt representation types.
    """

    OAI = "openai"
    REASONING = "reasoning"
