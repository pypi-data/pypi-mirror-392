"""
PACT Memory for LangChain - Emotional intelligence for your agents.

Part of PACT by NeurobloomAI
https://github.com/neurobloomai/pact-hx
"""

from .memory import PACTMemory, AsyncPACTMemory, create_pact_memory
from .client import PACTClient
from .version import __version__

__all__ = [
    "PACTMemory",
    "AsyncPACTMemory", 
    "PACTClient",
    "create_pact_memory",
    "__version__",
]
