from enum import Enum


class Enum__Classification__Output_Mode(str, Enum):                            # Output format options for classification results
    HASHES_ONLY      = 'hashes-only'                                           # Return only hash IDs
    HASHES_WITH_TEXT = 'hashes-with-text'                                      # Return hash IDs with original text
    FULL_RATINGS     = 'full-ratings'                                          # Return everything including scores
    SEPARATED        = 'separated'                                             # Return positive/negative in separate lists
    COMBINED         = 'combined'                                              # Return single list with ratings
