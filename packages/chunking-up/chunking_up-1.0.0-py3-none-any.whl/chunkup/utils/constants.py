"""All the CHONKY goodness in one place"""

MASCOT = r"""
      ∧___∧
     (  ´∀｀) つ━☆・*。   CHONK!
     ⊂  ノ     ・゜+.        
      しーJ    °。+ *´¨)   Pygmy Hippo Power!
                .· ´¸.·*´¨) ¸.·*¨)
                (¸.·´ (¸.·'* ☆ CHONK CHONK!
"""

CHONK_SPEED = "⚡ Speed of Light CHONKING activated!"

SUPPORTED_LANGUAGES = [
    "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh-cn", "zh-tw",
    "ar", "hi", "tr", "nl", "pl", "sv", "da", "no", "fi", "cs", "hu", "bg",
    "hr", "et", "el", "he", "ga", "is", "id", "lv", "lt", "ms", "mt", "fa",
    "ro", "sk", "sl", "th", "uk", "vi", "cy", "yi", "af", "sq", "am", "hy",
    "az", "eu", "bn", "bs", "ca", "ceb", "co", "eo", "fy", "gl", "ka", "ku"
]

VECTOR_DBS = [
    "pinecone", "weaviate", "qdrant", "milvus", "chroma",
    "faiss", "annoy", "elasticsearch", "redis", "mongodb"
]

INTEGRATIONS = [
    "openai", "anthropic", "cohere", "huggingface", "vertex_ai",
    "aws_bedrock", "azure_openai", "llama_cpp", "ollama"
] + VECTOR_DBS + [
    "langchain", "llamaindex", "haystack", "semantic_kernel"
]