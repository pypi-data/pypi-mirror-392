from osbot_utils.type_safe.primitives.core.Safe_Float import Safe_Float

class Safe_Float__Topic_Confidence(Safe_Float):                                # Topic classification confidence score (0.0-1.0)
    min_value = 0.0                                                            # Minimum confidence (no match)
    max_value = 1.0                                                            # Maximum confidence (perfect match)
