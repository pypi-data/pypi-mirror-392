"""
Type-Safe Model Constants for Cost Katana Python SDK

Use these constants instead of strings to prevent typos and get IDE autocomplete.

Example:
    import cost_katana as ck
    from cost_katana.models_constants import openai, anthropic, google
    
    # Type-safe model selection (recommended)
    response = ck.ai(openai.gpt_4, 'Hello world')
    
    # Old way still works but shows deprecation warning
    response = ck.ai('gpt-4', 'Hello world')
"""


# ============================================================================
# OPENAI MODELS
# ============================================================================

class openai:
    """OpenAI model constants"""
    
    # GPT-5 Series
    gpt_5 = 'gpt-5'
    gpt_5_mini = 'gpt-5-mini'
    gpt_5_nano = 'gpt-5-nano'
    gpt_5_pro = 'gpt-5-pro'
    gpt_5_codex = 'gpt-5-codex'
    gpt_5_chat_latest = 'gpt-5-chat-latest'
    
    # GPT-4.1 Series
    gpt_4_1 = 'gpt-4.1'
    gpt_4_1_mini = 'gpt-4.1-mini'
    gpt_4_1_nano = 'gpt-4.1-nano'
    
    # GPT-4o Series
    gpt_4o = 'gpt-4o'
    gpt_4o_2024_08_06 = 'gpt-4o-2024-08-06'
    gpt_4o_2024_05_13 = 'gpt-4o-2024-05-13'
    gpt_4o_audio_preview = 'gpt-4o-audio-preview'
    gpt_4o_realtime_preview = 'gpt-4o-realtime-preview'
    gpt_4o_mini = 'gpt-4o-mini'
    gpt_4o_mini_2024_07_18 = 'gpt-4o-mini-2024-07-18'
    gpt_4o_mini_audio_preview = 'gpt-4o-mini-audio-preview'
    gpt_4o_mini_realtime_preview = 'gpt-4o-mini-realtime-preview'
    
    # O-Series Models
    o3_pro = 'o3-pro'
    o3_deep_research = 'o3-deep-research'
    o4_mini = 'o4-mini'
    o4_mini_deep_research = 'o4-mini-deep-research'
    o3 = 'o3'
    o1_pro = 'o1-pro'
    o1 = 'o1'
    o3_mini = 'o3-mini'
    o1_mini = 'o1-mini'
    o1_preview = 'o1-preview'
    
    # Video Generation
    sora_2 = 'sora-2'
    sora_2_pro = 'sora-2-pro'
    
    # Image Generation
    gpt_image_1 = 'gpt-image-1'
    gpt_image_1_mini = 'gpt-image-1-mini'
    dall_e_3 = 'dall-e-3'
    dall_e_2 = 'dall-e-2'
    
    # Audio & Realtime
    gpt_realtime = 'gpt-realtime'
    gpt_realtime_mini = 'gpt-realtime-mini'
    gpt_audio = 'gpt-audio'
    gpt_audio_mini = 'gpt-audio-mini'
    
    # Transcription
    gpt_4o_transcribe = 'gpt-4o-transcribe'
    gpt_4o_transcribe_diarize = 'gpt-4o-transcribe-diarize'
    gpt_4o_mini_transcribe = 'gpt-4o-mini-transcribe'
    whisper_1 = 'whisper-1'
    
    # Text-to-Speech
    gpt_4o_mini_tts = 'gpt-4o-mini-tts'
    tts_1 = 'tts-1'
    tts_1_hd = 'tts-1-hd'
    
    # Open-Weight Models
    gpt_oss_120b = 'gpt-oss-120b'
    gpt_oss_20b = 'gpt-oss-20b'
    
    # Specialized
    codex_mini_latest = 'codex-mini-latest'
    omni_moderation_latest = 'omni-moderation-latest'
    gpt_4o_mini_search_preview = 'gpt-4o-mini-search-preview-2025-03-11'
    gpt_4o_search_preview = 'gpt-4o-search-preview-2025-03-11'
    computer_use_preview = 'computer-use-preview-2025-03-11'
    
    # Embeddings
    text_embedding_3_small = 'text-embedding-3-small'
    text_embedding_3_large = 'text-embedding-3-large'
    text_embedding_ada_002 = 'text-embedding-ada-002'
    
    # ChatGPT Models
    chatgpt_4o_latest = 'chatgpt-4o-latest'
    
    # Legacy Models
    gpt_4_turbo = 'gpt-4-turbo'
    gpt_4 = 'gpt-4'
    gpt_3_5_turbo = 'gpt-3.5-turbo'
    gpt_3_5_turbo_0125 = 'gpt-3.5-turbo-0125'


# ============================================================================
# ANTHROPIC MODELS
# ============================================================================

class anthropic:
    """Anthropic model constants"""
    
    # Claude 4.5 Series
    claude_sonnet_4_5 = 'claude-sonnet-4-5'
    claude_haiku_4_5 = 'claude-haiku-4-5'
    
    # Claude 4 Series
    claude_opus_4_1_20250805 = 'claude-opus-4-1-20250805'
    claude_opus_4_20250514 = 'claude-opus-4-20250514'
    claude_sonnet_4_20250514 = 'claude-sonnet-4-20250514'
    
    # Claude 3.7 Series
    claude_3_7_sonnet_20250219 = 'claude-3-7-sonnet-20250219'
    
    # Claude 3.5 Series
    claude_3_5_sonnet_20241022 = 'claude-3-5-sonnet-20241022'
    claude_3_5_haiku_20241022 = 'claude-3-5-haiku-20241022'
    
    # Claude 3 Series
    claude_3_haiku_20240307 = 'claude-3-haiku-20240307'
    claude_3_opus_20240229 = 'claude-3-opus-20240229'


# ============================================================================
# GOOGLE (GEMINI) MODELS
# ============================================================================

class google:
    """Google AI model constants"""
    
    # Gemini 2.5 Series
    gemini_2_5_pro = 'gemini-2.5-pro'
    gemini_2_5_flash = 'gemini-2.5-flash'
    gemini_2_5_flash_lite_preview = 'gemini-2.5-flash-lite-preview'
    gemini_2_5_flash_lite = 'gemini-2.5-flash-lite'
    gemini_2_5_flash_audio = 'gemini-2.5-flash-audio'
    gemini_2_5_flash_lite_audio_preview = 'gemini-2.5-flash-lite-audio-preview'
    gemini_2_5_flash_native_audio = 'gemini-2.5-flash-native-audio'
    gemini_2_5_flash_native_audio_output = 'gemini-2.5-flash-native-audio-output'
    gemini_2_5_flash_preview_tts = 'gemini-2.5-flash-preview-tts'
    gemini_2_5_pro_preview_tts = 'gemini-2.5-pro-preview-tts'
    
    # Gemini 2.0 Series
    gemini_2_0_flash = 'gemini-2.0-flash'
    gemini_2_0_flash_lite = 'gemini-2.0-flash-lite'
    gemini_2_0_flash_audio = 'gemini-2.0-flash-audio'
    
    # Gemini 1.5 Series
    gemini_1_5_flash = 'gemini-1.5-flash'
    gemini_1_5_flash_large_context = 'gemini-1.5-flash-large-context'
    gemini_1_5_flash_8b = 'gemini-1.5-flash-8b'
    gemini_1_5_flash_8b_large_context = 'gemini-1.5-flash-8b-large-context'
    gemini_1_5_pro = 'gemini-1.5-pro'
    gemini_1_5_pro_large_context = 'gemini-1.5-pro-large-context'
    
    # Gemini 1.0 Series
    gemini_1_0_pro = 'gemini-1.0-pro'
    gemini_1_0_pro_vision = 'gemini-1.0-pro-vision'
    
    # Legacy Names
    gemini_pro = 'gemini-pro'
    gemini_pro_vision = 'gemini-pro-vision'
    
    # Gemma Models (Open Source)
    gemma_3n = 'gemma-3n'
    gemma_3 = 'gemma-3'
    gemma_2 = 'gemma-2'
    gemma = 'gemma'
    shieldgemma_2 = 'shieldgemma-2'
    paligemma = 'paligemma'
    codegemma = 'codegemma'
    txgemma = 'txgemma'
    medgemma = 'medgemma'
    medsiglip = 'medsiglip'
    t5gemma = 't5gemma'
    
    # Embeddings
    text_embedding_004 = 'text-embedding-004'
    multimodal_embeddings = 'multimodal-embeddings'
    
    # Imagen (Image Generation)
    imagen_4_generation = 'imagen-4-generation'
    imagen_4_fast_generation = 'imagen-4-fast-generation'
    imagen_4_ultra_generation = 'imagen-4-ultra-generation'
    imagen_3_generation = 'imagen-3-generation'
    imagen_3_editing_customization = 'imagen-3-editing-customization'
    imagen_3_fast_generation = 'imagen-3-fast-generation'
    imagen_captioning_vqa = 'imagen-captioning-vqa'
    
    # Veo (Video Generation)
    veo_2 = 'veo-2'
    veo_3 = 'veo-3'
    veo_3_fast = 'veo-3-fast'
    veo_3_preview = 'veo-3-preview'
    veo_3_fast_preview = 'veo-3-fast-preview'
    
    # Preview Models
    virtual_try_on = 'virtual-try-on'


# ============================================================================
# AWS BEDROCK MODELS
# ============================================================================

class aws_bedrock:
    """AWS Bedrock model constants"""
    
    # Amazon Nova Models
    nova_pro = 'amazon.nova-pro-v1:0'
    nova_lite = 'amazon.nova-lite-v1:0'
    nova_micro = 'amazon.nova-micro-v1:0'
    
    # Anthropic Claude on Bedrock
    claude_sonnet_4_5 = 'anthropic.claude-sonnet-4-5-v1:0'
    claude_haiku_4_5 = 'anthropic.claude-haiku-4-5-v1:0'
    claude_opus_4_1_20250805 = 'anthropic.claude-opus-4-1-20250805-v1:0'
    claude_opus_4_20250514 = 'anthropic.claude-opus-4-20250514-v1:0'
    claude_sonnet_4_20250514 = 'anthropic.claude-sonnet-4-20250514-v1:0'
    claude_3_7_sonnet_20250219 = 'anthropic.claude-3-7-sonnet-20250219-v1:0'
    claude_3_5_sonnet_20241022 = 'anthropic.claude-3-5-sonnet-20241022-v1:0'
    claude_3_5_sonnet_20240620 = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    claude_3_5_haiku_20241022 = 'anthropic.claude-3-5-haiku-20241022-v1:0'
    claude_3_haiku_20240307 = 'anthropic.claude-3-haiku-20240307-v1:0'
    claude_3_opus_20240229 = 'anthropic.claude-3-opus-20240229-v1:0'
    
    # Inference Profiles
    us_claude_3_5_haiku_20241022 = 'us.anthropic.claude-3-5-haiku-20241022-v1:0'
    
    # Meta Llama Models on Bedrock
    llama_3_3_70b_instruct = 'meta.llama3-3-70b-instruct-v1:0'
    llama_3_2_1b_instruct = 'meta.llama3-2-1b-instruct-v1:0'
    llama_3_2_3b_instruct = 'meta.llama3-2-3b-instruct-v1:0'
    llama_3_2_11b_vision_instruct = 'meta.llama3-2-11b-vision-instruct-v1:0'
    llama_3_2_90b_vision_instruct = 'meta.llama3-2-90b-vision-instruct-v1:0'
    llama_3_1_8b_instruct = 'meta.llama3-1-8b-instruct-v1:0'
    llama_3_1_70b_instruct = 'meta.llama3-1-70b-instruct-v1:0'
    llama_3_1_405b_instruct = 'meta.llama3-1-405b-instruct-v1:0'
    
    # Mistral Models on Bedrock
    mistral_large_2 = 'mistral.mistral-large-2407-v1:0'
    mistral_small = 'mistral.mistral-small-2402-v1:0'
    
    # Cohere Models on Bedrock
    cohere_command_r = 'cohere.command-r-v1:0'
    cohere_command_r_plus = 'cohere.command-r-plus-v1:0'


# ============================================================================
# XAI (GROK) MODELS
# ============================================================================

class xai:
    """xAI model constants"""
    
    grok_2_1212 = 'grok-2-1212'
    grok_2_vision_1212 = 'grok-2-vision-1212'
    grok_beta = 'grok-beta'
    grok_vision_beta = 'grok-vision-beta'


# ============================================================================
# DEEPSEEK MODELS
# ============================================================================

class deepseek:
    """DeepSeek model constants"""
    
    deepseek_chat = 'deepseek-chat'
    deepseek_reasoner = 'deepseek-reasoner'


# ============================================================================
# MISTRAL MODELS
# ============================================================================

class mistral:
    """Mistral AI model constants"""
    
    mistral_large_latest = 'mistral-large-latest'
    mistral_small_latest = 'mistral-small-latest'
    codestral_latest = 'codestral-latest'
    ministral_8b_latest = 'ministral-8b-latest'
    ministral_3b_latest = 'ministral-3b-latest'
    pixtral_large_latest = 'pixtral-large-latest'
    pixtral_12b = 'pixtral-12b-2409'


# ============================================================================
# COHERE MODELS
# ============================================================================

class cohere:
    """Cohere model constants"""
    
    command_r_plus = 'command-r-plus'
    command_r = 'command-r'
    command_r_plus_08_2024 = 'command-r-plus-08-2024'
    command_r_08_2024 = 'command-r-08-2024'
    command_light = 'command-light'
    embed_english_v3 = 'embed-english-v3.0'
    embed_multilingual_v3 = 'embed-multilingual-v3.0'
    embed_english_light_v3 = 'embed-english-light-v3.0'
    embed_multilingual_light_v3 = 'embed-multilingual-light-v3.0'
    rerank_english_v3 = 'rerank-english-v3.0'
    rerank_multilingual_v3 = 'rerank-multilingual-v3.0'


# ============================================================================
# GROQ MODELS
# ============================================================================

class groq:
    """Groq model constants"""
    
    llama_3_3_70b_versatile = 'llama-3.3-70b-versatile'
    llama_3_1_8b_instant = 'llama-3.1-8b-instant'
    llama_3_1_70b_versatile = 'llama-3.1-70b-versatile'
    llama_3_2_1b_preview = 'llama-3.2-1b-preview'
    llama_3_2_3b_preview = 'llama-3.2-3b-preview'
    llama_3_2_11b_vision_preview = 'llama-3.2-11b-vision-preview'
    llama_3_2_90b_vision_preview = 'llama-3.2-90b-vision-preview'
    mixtral_8x7b_32768 = 'mixtral-8x7b-32768'
    gemma_2_9b_it = 'gemma2-9b-it'
    gemma_7b_it = 'gemma-7b-it'


# ============================================================================
# META MODELS
# ============================================================================

class meta:
    """Meta model constants"""
    
    llama_3_3_70b_instruct = 'llama-3.3-70b-instruct'
    llama_3_2_1b_instruct = 'llama-3.2-1b-instruct'
    llama_3_2_3b_instruct = 'llama-3.2-3b-instruct'
    llama_3_2_11b_vision_instruct = 'llama-3.2-11b-vision-instruct'
    llama_3_2_90b_vision_instruct = 'llama-3.2-90b-vision-instruct'
    llama_3_1_8b_instruct = 'llama-3.1-8b-instruct'
    llama_3_1_70b_instruct = 'llama-3.1-70b-instruct'
    llama_3_1_405b_instruct = 'llama-3.1-405b-instruct'


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Collect all model values
_ALL_MODEL_VALUES = set()

for cls in [openai, anthropic, google, aws_bedrock, xai, deepseek, mistral, cohere, groq, meta]:
    for attr in dir(cls):
        if not attr.startswith('_'):
            value = getattr(cls, attr)
            if isinstance(value, str):
                _ALL_MODEL_VALUES.add(value)


def is_model_constant(value: str) -> bool:
    """
    Check if a string is a known model constant value.
    
    Args:
        value: The model string to check
        
    Returns:
        True if the value matches a known model constant
    """
    return value in _ALL_MODEL_VALUES


def get_all_model_constants() -> list:
    """
    Get all available model constants as a list.
    
    Returns:
        List of all model constant values
    """
    return list(_ALL_MODEL_VALUES)


def get_provider_from_model(model_id: str) -> str:
    """
    Get provider name from model ID.
    
    Args:
        model_id: The model ID to check
        
    Returns:
        Provider name or 'unknown'
    """
    # Check each class's attributes
    for attr in dir(openai):
        if not attr.startswith('_') and getattr(openai, attr, None) == model_id:
            return 'OpenAI'
    
    for attr in dir(anthropic):
        if not attr.startswith('_') and getattr(anthropic, attr, None) == model_id:
            return 'Anthropic'
    
    for attr in dir(google):
        if not attr.startswith('_') and getattr(google, attr, None) == model_id:
            return 'Google AI'
    
    for attr in dir(aws_bedrock):
        if not attr.startswith('_') and getattr(aws_bedrock, attr, None) == model_id:
            return 'AWS Bedrock'
    
    for attr in dir(xai):
        if not attr.startswith('_') and getattr(xai, attr, None) == model_id:
            return 'xAI'
    
    for attr in dir(deepseek):
        if not attr.startswith('_') and getattr(deepseek, attr, None) == model_id:
            return 'DeepSeek'
    
    for attr in dir(mistral):
        if not attr.startswith('_') and getattr(mistral, attr, None) == model_id:
            return 'Mistral AI'
    
    for attr in dir(cohere):
        if not attr.startswith('_') and getattr(cohere, attr, None) == model_id:
            return 'Cohere'
    
    for attr in dir(groq):
        if not attr.startswith('_') and getattr(groq, attr, None) == model_id:
            return 'Groq'
    
    for attr in dir(meta):
        if not attr.startswith('_') and getattr(meta, attr, None) == model_id:
            return 'Meta'
    
    return 'unknown'


__all__ = [
    'openai',
    'anthropic',
    'google',
    'aws_bedrock',
    'xai',
    'deepseek',
    'mistral',
    'cohere',
    'groq',
    'meta',
    'is_model_constant',
    'get_all_model_constants',
    'get_provider_from_model',
]

