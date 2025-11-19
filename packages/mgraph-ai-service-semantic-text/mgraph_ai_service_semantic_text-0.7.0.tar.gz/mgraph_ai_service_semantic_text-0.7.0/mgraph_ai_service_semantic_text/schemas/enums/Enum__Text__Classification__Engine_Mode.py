from enum import Enum


class Enum__Text__Classification__Engine_Mode(str, Enum):                      # Engine modes for text classification
    AWS_COMPREHEND = 'aws_comprehend'                                          # AWS Comprehend ML-based sentiment analysis (real NLP)
    TEXT_HASH      = 'text_hash'                                               # Hash-based deterministic pseudo-random classification
    RANDOM         = 'random'                                                  # Pure random classification (distribution)
    LLM_SINGLE     = 'llm_single'                                              # Single LLM call per text (future)
    LLM_MULTIPLE   = 'llm_multiple'                                            # Multiple LLM calls for consensus (future)
