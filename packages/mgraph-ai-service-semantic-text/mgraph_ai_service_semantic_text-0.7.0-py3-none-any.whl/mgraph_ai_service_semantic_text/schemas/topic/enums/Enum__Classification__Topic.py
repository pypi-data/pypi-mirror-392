from enum import Enum


class Enum__Classification__Topic(str, Enum):                                  # Predefined topic categories for text classification
    # Technology (3 topics)
    TECHNOLOGY_SOFTWARE      = 'technology-software'                           # Software development, programming, apps
    TECHNOLOGY_HARDWARE      = 'technology-hardware'                           # Hardware, devices, electronics
    TECHNOLOGY_AI_ML         = 'technology-ai_ml'                              # AI, machine learning, data science
    
    # Business (3 topics)
    BUSINESS_FINANCE         = 'business-finance'                              # Finance, banking, investments
    BUSINESS_MARKETING       = 'business-marketing'                            # Marketing, advertising, branding
    BUSINESS_OPERATIONS      = 'business-operations'                           # Operations, management, processes
    
    # Health (3 topics)
    HEALTH_MEDICAL           = 'health-medical'                                # Medical, healthcare, treatments
    HEALTH_WELLNESS          = 'health-wellness'                               # Fitness, nutrition, well-being
    HEALTH_MENTAL            = 'health-mental'                                 # Mental health, psychology, therapy
    
    # Education (3 topics)
    EDUCATION_ACADEMIC       = 'education-academic'                            # Academia, research, learning
    EDUCATION_TRAINING       = 'education-training'                            # Professional training, skills
    EDUCATION_ONLINE         = 'education-online'                              # E-learning, online courses
    
    # General (3 topics)
    GENERAL_NEWS             = 'general-news'                                  # News, current events, journalism
    GENERAL_ENTERTAINMENT    = 'general-entertainment'                         # Entertainment, media, culture
    GENERAL_LIFESTYLE        = 'general-lifestyle'                             # Lifestyle, hobbies, personal
