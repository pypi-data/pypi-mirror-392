"""Plugin registry for 32+ integrations 🔌"""

from typing import Dict, Type, Any, Optional
from functools import lru_cache

# Registry of all integrations
_INTEGRATION_REGISTRY = {
    # Vector DBs
    "vector_dbs": {
        "pinecone": "chunkup.integrations.vector_dbs.pinecone.PineconeIntegration",
        "qdrant": "chunkup.integrations.vector_dbs.qdrant.QdrantIntegration",
        "weaviate": "chunkup.integrations.vector_dbs.weaviate.WeaviateIntegration",
        "chroma": "chunkup.integrations.vector_dbs.chroma.ChromaIntegration",
        "milvus": "chunkup.integrations.vector_dbs.milvus.MilvusIntegration",
        "faiss": "chunkup.integrations.vector_dbs.faiss.FaissIntegration",
        "annoy": "chunkup.integrations.vector_dbs.annoy.AnnoyIntegration",
        "elasticsearch": "chunkup.integrations.vector_dbs.elasticsearch.ElasticsearchIntegration",
        "redis": "chunkup.integrations.vector_dbs.redis.RedisIntegration",
        "mongodb": "chunkup.integrations.vector_dbs.mongodb.MongoDBIntegration",
        "supabase": "chunkup.integrations.vector_dbs.supabase.SupabaseIntegration",
        "pgvector": "chunkup.integrations.vector_dbs.pgvector.PGVectorIntegration",
        "singlestore": "chunkup.integrations.vector_dbs.singlestore.SingleStoreIntegration",
        "clickhouse": "chunkup.integrations.vector_dbs.clickhouse.ClickHouseIntegration",
        "neo4j": "chunkup.integrations.vector_dbs.neo4j.Neo4jIntegration",
        "cassandra": "chunkup.integrations.vector_dbs.cassandra.CassandraIntegration",
        "dynamodb": "chunkup.integrations.vector_dbs.dynamodb.DynamoDBIntegration",
    },
    # Embedders
    "embedders": {
        "openai": "chunkup.integrations.embedders.openai.OpenAIEmbedder",
        "cohere": "chunkup.integrations.embedders.cohere.CohereEmbedder",
        "huggingface": "chunkup.integrations.embedders.huggingface.HuggingFaceEmbedder",
        "vertex": "chunkup.integrations.embedders.vertex.VertexEmbedder",
        "anthropic": "chunkup.integrations.embedders.anthropic.AnthropicEmbedder",
        "aws_bedrock": "chunkup.integrations.embedders.aws_bedrock.BedrockEmbedder",
        "azure_openai": "chunkup.integrations.embedders.azure_openai.AzureOpenAIEmbedder",
        "ollama": "chunkup.integrations.embedders.ollama.OllamaEmbedder",
        "llama_cpp": "chunkup.integrations.embedders.llama_cpp.LlamaCppEmbedder",
        "voyage": "chunkup.integrations.embedders.voyage.VoyageEmbedder",
        "jina": "chunkup.integrations.embedders.jina.JinaEmbedder",
    },
    # Loaders
    "loaders": {
        "http": "chunkup.integrations.loaders.http.HTTPIntegration",
        "s3": "chunkup.integrations.loaders.s3.S3Integration",
        "gcs": "chunkup.integrations.loaders.gcs.GCSIntegration",
        "azure_blob": "chunkup.integrations.loaders.azure_blob.AzureBlobIntegration",
        "notion": "chunkup.integrations.loaders.notion.NotionIntegration",
        "github": "chunkup.integrations.loaders.github.GitHubIntegration",
        "gitlab": "chunkup.integrations.loaders.gitlab.GitLabIntegration",
        "youtube": "chunkup.integrations.loaders.youtube.YouTubeIntegration",
        "dropbox": "chunkup.integrations.loaders.dropbox.DropboxIntegration",
        "onedrive": "chunkup.integrations.loaders.onedrive.OneDriveIntegration",
        "slack": "chunkup.integrations.loaders.slack.SlackIntegration",
        "discord": "chunkup.integrations.loaders.discord.DiscordIntegration",
        "confluence": "chunkup.integrations.loaders.confluence.ConfluenceIntegration",
        "sharepoint": "chunkup.integrations.loaders.sharepoint.SharePointIntegration",
    }
}


@lru_cache(maxsize=128)
def get_integration(category: str, name: str) -> Any:
    """Lazy-load an integration class"""
    try:
        module_path = _INTEGRATION_REGISTRY[category][name]
        from importlib import import_module

        parts = module_path.split(".")
        module_name = ".".join(parts[:-1])
        class_name = parts[-1]

        module = import_module(module_name)
        return getattr(module, class_name)

    except KeyError:
        raise ValueError(f"Integration '{name}' not found in category '{category}'")
    except ImportError as e:
        raise ImportError(f"Failed to load integration '{name}': {e}. Did you install the required dependencies?")


def list_integrations(category: Optional[str] = None) -> Dict[str, list]:
    """List all available integrations"""
    if category:
        return {category: list(_INTEGRATION_REGISTRY.get(category, {}).keys())}

    return {cat: list(integrations.keys()) for cat, integrations in _INTEGRATION_REGISTRY.items()}


def check_integration_available(category: str, name: str) -> bool:
    """Check if integration is available (dependencies installed)"""
    try:
        get_integration(category, name)
        return True
    except (ImportError, ValueError):
        return False