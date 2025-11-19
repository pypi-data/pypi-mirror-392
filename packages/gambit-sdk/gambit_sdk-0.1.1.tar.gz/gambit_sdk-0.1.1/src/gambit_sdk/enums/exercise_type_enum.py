from enum import Enum


class ExerciseType(Enum):
    CHOICE_SINGLE = "choice_single"
    CHOICE_MULTIPLE = "choice_multiple"
    INPUT_STRING = "input_string"
    INPUT_TEXT = "input_text"
    TEXT_FILE = "text_file"
    MATCHING_PAIRS = "matching_pairs"
    SEQUENCE_ORDERING = "sequence_ordering"
    UNSUPPORTED = "unsupported"
