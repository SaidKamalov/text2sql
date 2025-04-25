from enum import Enum


class ShemaInfoOptions(Enum):
    """
    Enum class for schema information options.
    """

    FULL_SCHEMA = "full schema"
    LINKED_SCHEMA = "linked schema"


class ExampleSelectionType(Enum):
    COSINE_SIM = "cosine_sim"
    RANDOM = "random"
    RAND_HARDNESS = "random hardness"
    COSINE_SIM_HARDNESS = "cosine sim hardness"
