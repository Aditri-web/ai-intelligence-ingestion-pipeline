"""
Seed Database of 50+ Known Canonical AI Organizations & Products.
Used as the reference dictionary for deterministic entity canonicalization and alias mapping.
"""

CANONICAL_SEED_ENTITIES = {
    # Organization Name -> Dictionary of Aliases & Metadata
    "OpenAI": {
        "aliases": ["openai", "openai inc", "open ai", "openai inc.", "open-ai", "openai, inc."],
        "type": "STARTUP",
        "employee_range": "1000-5000"
    },
    "Anthropic": {
        "aliases": ["anthropic", "anthropic pbc", "anthropic ai", "anthropic, pbc"],
        "type": "STARTUP",
        "employee_range": "500-1000"
    },
    "Cohere": {
        "aliases": ["cohere", "cohere ai", "cohere inc", "cohere inc."],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "Mistral AI": {
        "aliases": ["mistral", "mistral ai", "mistralai", "mistral.ai"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Hugging Face": {
        "aliases": ["huggingface", "hugging face", "hugging face inc", "huggingface inc."],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "Scale AI": {
        "aliases": ["scale ai", "scale.ai", "scaleai", "scale inc"],
        "type": "STARTUP",
        "employee_range": "500-1000"
    },
    "Midjourney": {
        "aliases": ["midjourney", "midjourney inc", "midjourney.com"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Perplexity AI": {
        "aliases": ["perplexity", "perplexity ai", "perplexity.ai", "perplexity inc"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Jasper AI": {
        "aliases": ["jasper", "jasper ai", "jasper.ai", "usejasper"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "RunwayML": {
        "aliases": ["runway", "runwayml", "runway ml", "runway research"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Stability AI": {
        "aliases": ["stability ai", "stability.ai", "stabilityai", "stability inc"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Inflection AI": {
        "aliases": ["inflection", "inflection ai", "inflection.ai"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Character.AI": {
        "aliases": ["character ai", "character.ai", "characterai", "character ai inc"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "EleutherAI": {
        "aliases": ["eleutherai", "eleuther ai", "eleuther.ai"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Together AI": {
        "aliases": ["together ai", "together.ai", "togetherai", "together xyz"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Anyscale": {
        "aliases": ["anyscale", "anyscale inc", "anyscale.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Pinecone": {
        "aliases": ["pinecone", "pinecone io", "pinecone.io", "pinecone systems"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Weaviate": {
        "aliases": ["weaviate", "weaviate io", "weaviate.io", "semi technologies"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Qdrant": {
        "aliases": ["qdrant", "qdrant tech", "qdrant.tech"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Chroma": {
        "aliases": ["chroma", "chromadb", "chroma db", "trychroma"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "LangChain": {
        "aliases": ["langchain", "langchain inc", "langchain.com", "langchain ai"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "LlamaIndex": {
        "aliases": ["llamaindex", "llama index", "gpt-index", "llamaindex ai"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Weights & Biases": {
        "aliases": ["wandb", "weights & biases", "weights and biases", "wandb.ai"],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "DeepL": {
        "aliases": ["deepl", "deepl gmbh", "deepl.com", "deepl translator"],
        "type": "STARTUP",
        "employee_range": "500-1000"
    },
    "Synthesia": {
        "aliases": ["synthesia", "synthesia io", "synthesia.io"],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "ElevenLabs": {
        "aliases": ["elevenlabs", "eleven labs", "elevenlabs.io"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Harvey AI": {
        "aliases": ["harvey", "harvey ai", "harvey.ai"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Abridge": {
        "aliases": ["abridge", "abridge AI", "abridge.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Hippocratic AI": {
        "aliases": ["hippocratic", "hippocratic ai", "hippocratic.ai"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Glean": {
        "aliases": ["glean", "glean technologies", "glean.com"],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "CodiumAI": {
        "aliases": ["codiumai", "codium ai", "codium.ai", "qodo"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Cursor": {
        "aliases": ["cursor", "cursor sh", "anysphere", "anysphere inc"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Replit": {
        "aliases": ["replit", "replit inc", "replit.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Poolside AI": {
        "aliases": ["poolside", "poolside ai", "poolside.ai"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Cognition AI": {
        "aliases": ["cognition", "cognition ai", "devin", "cognition.ai"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Groq": {
        "aliases": ["groq", "groq inc", "groq.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "Cerebras": {
        "aliases": ["cerebras", "cerebras systems", "cerebras.net"],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "SambaNova": {
        "aliases": ["sambanova", "sambanova systems", "sambanova.ai"],
        "type": "STARTUP",
        "employee_range": "250-500"
    },
    "Fireworks AI": {
        "aliases": ["fireworks", "fireworks ai", "fireworks.ai"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Baseten": {
        "aliases": ["baseten", "baseten.co", "baseten inc"],
        "type": "STARTUP",
        "employee_range": "50-100"
    },
    "Modal": {
        "aliases": ["modal", "modal labs", "modal.com"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Replicate": {
        "aliases": ["replicate", "replicate com", "replicate.com"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Fal.ai": {
        "aliases": ["fal", "fal ai", "fal.ai", "features analytics lab"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Vellum": {
        "aliases": ["vellum", "vellum ai", "vellum.ai"],
        "type": "STARTUP",
        "employee_range": "20-50"
    },
    "Arize AI": {
        "aliases": ["arize", "arize ai", "arize.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "HoneyHive": {
        "aliases": ["honeyhive", "honeyhive ai", "honeyhive.ai"],
        "type": "STARTUP",
        "employee_range": "10-20"
    },
    "Portkey AI": {
        "aliases": ["portkey", "portkey ai", "portkey.ai"],
        "type": "STARTUP",
        "employee_range": "10-20"
    },
    "AgentOps": {
        "aliases": ["agentops", "agentops ai", "agentops.ai"],
        "type": "STARTUP",
        "employee_range": "10-20"
    },
    "Deepgram": {
        "aliases": ["deepgram", "deepgram inc", "deepgram.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    },
    "AssemblyAI": {
        "aliases": ["assemblyai", "assembly ai", "assemblyai.com"],
        "type": "STARTUP",
        "employee_range": "100-250"
    }
}
