# 🧠 PACT for LangChain

**Drop-in memory replacement that makes your agents remember what matters.**

[![PyPI version](https://badge.fury.io/py/pact-langchain.svg)](https://badge.fury.io/py/pact-langchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/pact-langchain)](https://pepy.tech/project/pact-langchain)

---

## The Problem

Your LangChain agent forgets things. Important things.

```python
# Standard LangChain memory
conversation.memory.save_context(
    {"input": "I'm really frustrated with this bug"}, 
    {"output": "I understand. Let's debug it."}
)

# 10 messages later...
conversation.memory.load_memory_variables({})
# Returns: Everything, including irrelevant details
# Missing: The emotional context that matters
```

**Result:** Your agent treats every message the same. No emotional awareness. No prioritization. Just a wall of text.

---

## The Solution

PACT Memory tracks **what matters** - emotions, context, and relationships.

```python
from pact_langchain import PACTMemory

memory = PACTMemory(api_key="your_key")
conversation = ConversationChain(llm=llm, memory=memory)

# Same interface, better memory
conversation.predict(input="I'm really frustrated with this bug")
# PACT tracks: emotional_state="frustrated", priority="high"

# 10 messages later...
memory.load_memory_variables({})
# Returns: Relevant context + emotional state + consolidated summary
# Your agent knows the user is frustrated and prioritizes accordingly
```

---

## Installation

```bash
pip install pact-langchain
```

**Requirements:**
- Python 3.8+
- LangChain 0.1.0+
- PACT API key (get one at [neurobloom.ai](https://neurobloom.ai))

---

## Quick Start

## Quick Start
```python
pip install pact-langchain

from pact_langchain import PACTMemory

# Use with deployed API
memory = PACTMemory(
    api_key="your-key",
    api_url="https://pact-hx.onrender.com"  # Live API!
)

# Save conversation
memory.save_context(
    {"input": "Hello!"},
    {"output": "Hi there!"}
)

# Load context
context = memory.load_memory_variables({})
```

### Basic Usage (Drop-in Replacement)

```python
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from pact_langchain import PACTMemory

# Replace this:
# from langchain.memory import ConversationBufferMemory
# memory = ConversationBufferMemory()

# With this:
memory = PACTMemory(api_key="sk_test_...")

# Everything else stays the same
llm = OpenAI(temperature=0.7)
conversation = ConversationChain(llm=llm, memory=memory)

conversation.predict(input="Hi, I'm working on a Python project")
conversation.predict(input="I'm stuck on async functions")
conversation.predict(input="This is really frustrating!")

# PACT automatically:
# ✅ Tracks emotional progression (calm → frustrated)
# ✅ Identifies key topics (Python, async, debugging)
# ✅ Consolidates old context to save tokens
```

### With Emotional Context

```python
memory = PACTMemory(
    api_key="sk_test_...",
    emotional_tracking=True,
    return_emotional_context=True
)

conversation = ConversationChain(llm=llm, memory=memory)

conversation.predict(input="I just got promoted!")
# Behind the scenes: emotional_state="excited", valence=0.8

# Access emotional state directly
state = memory.get_emotional_state()
print(state)
# {
#   "current_emotion": "excited",
#   "valence": 0.8,
#   "trend": "positive",
#   "key_emotions": ["joy", "pride"]
# }
```
### With Context Consolidation

```python
memory = PACTMemory(
    api_key="sk_test_...",
    context_consolidation=True,
    consolidation_threshold=10  # Consolidate after 10 messages
)

# After 10 messages, PACT automatically:
# 1. Summarizes old context
# 2. Keeps recent messages
# 3. Preserves emotional and topical highlights
# 4. Saves you tokens 💰

# Force consolidation manually
summary = memory.force_consolidation()
print(summary["consolidated_summary"])
# "User is debugging a Python async issue, feeling frustrated but making progress..."
```

---

## Side-by-Side Comparison

### Standard LangChain Memory

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
memory.save_context(
    {"input": "I'm excited about this project!"}, 
    {"output": "That's great!"}
)
memory.save_context(
    {"input": "Actually, I'm really stressed now."}, 
    {"output": "I can help with that."}
)

# Load memory
context = memory.load_memory_variables({})
print(context["history"])
# Human: I'm excited about this project!
# AI: That's great!
# Human: Actually, I'm really stressed now.
# AI: I can help with that.

# ❌ No emotional tracking
# ❌ No context prioritization
# ❌ No consolidation
# ❌ Grows unbounded (token explosion)
```

### PACT Memory

```python
from pact_langchain import PACTMemory

memory = PACTMemory(api_key="sk_test_...")
memory.save_context(
    {"input": "I'm excited about this project!"}, 
    {"output": "That's great!"}
)
memory.save_context(
    {"input": "Actually, I'm really stressed now."}, 
    {"output": "I can help with that."}
)

# Load memory
context = memory.load_memory_variables({})
print(context["history"])
# [Same conversation history]

print(context["emotional_state"])
# "stressed" (tracks emotional shift)

print(context["context_summary"])
# "User's emotional state shifted from excited to stressed regarding project"

# ✅ Emotional tracking
# ✅ Context prioritization
# ✅ Automatic consolidation
# ✅ Token-efficient
```

---

## Features

| Feature | Standard LangChain | PACT Memory |
|---------|-------------------|-------------|
| **Drop-in replacement** | ✅ | ✅ |
| **Emotional tracking** | ❌ | ✅ |
| **Context consolidation** | ❌ | ✅ |
| **Priority management** | ❌ | ✅ |
| **Token optimization** | ❌ | ✅ |
| **Relationship patterns** | ❌ | ✅ |
| **Memory visualization** | ❌ | ✅ |
| **Async support** | ✅ | ✅ |

---

## Advanced Usage

### Custom Configuration

```python
memory = PACTMemory(
    api_key="sk_test_...",
    
    # Emotional tracking
    emotional_tracking=True,
    return_emotional_context=True,
    
    # Context management
    context_consolidation=True,
    consolidation_threshold=15,  # Consolidate after N messages
    max_token_limit=2000,        # Max tokens in context
    
    # API settings
    api_url="https://api.neurobloom.ai/pact/v1"  # Custom endpoint
)
```

### Accessing Memory Graph

```python
# Get full memory graph structure
graph = memory.get_context_graph()

# Structure:
# {
#   "nodes": [
#     {"id": "msg_1", "type": "message", "content": "...", "emotion": "excited"},
#     {"id": "topic_python", "type": "topic", "importance": 0.9}
#   ],
#   "edges": [
#     {"from": "msg_1", "to": "topic_python", "type": "mentions"}
#   ]
# }

# Use this for visualization in your own UI
```

### Manual Priority Control

```python
# Mark important topics
memory.set_context_priority(topic="quarterly_goals", priority="high")
memory.set_context_priority(topic="lunch_preferences", priority="low")

# PACT will:
# - Keep high-priority context longer
# - Consolidate low-priority context sooner
# - Retrieve high-priority context first
```

### Async Support

```python
from pact_langchain import AsyncPACTMemory

memory = AsyncPACTMemory(api_key="sk_test_...")

# Use with async chains
async def chat():
    context = await memory.aload_memory_variables({})
    await memory.asave_context(
        {"input": "Hello"}, 
        {"output": "Hi there!"}
    )
```
---

## Real-World Example: Customer Support Bot

```python
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from pact_langchain import PACTMemory

# Initialize with emotional tracking
memory = PACTMemory(
    api_key="sk_prod_...",
    emotional_tracking=True,
    context_consolidation=True,
    consolidation_threshold=20
)

llm = OpenAI(temperature=0.7)
support_bot = ConversationChain(
    llm=llm, 
    memory=memory,
    verbose=True
)

# Customer conversation
support_bot.predict(input="My order hasn't arrived")
# PACT detects: emotion="concerned"

support_bot.predict(input="It's been 3 weeks!")
# PACT detects: emotion="frustrated", escalation=True

support_bot.predict(input="This is unacceptable!")
# PACT detects: emotion="angry", priority="high"

# Check emotional state
state = memory.get_emotional_state()
if state["current_emotion"] == "angry":
    # Escalate to human agent
    print("⚠️  Customer is angry - escalating to human agent")
    
# Get context summary for human agent
context = memory.load_memory_variables({})
print(context["context_summary"])
# "Customer ordered 3 weeks ago, item not delivered. 
#  Emotional progression: concerned → frustrated → angry"
```

---

## Comparison with Alternatives

### vs. ConversationBufferMemory
- ✅ PACT tracks emotions, buffer doesn't
- ✅ PACT consolidates context, buffer grows unbounded
- ✅ PACT prioritizes, buffer treats everything equal

### vs. ConversationSummaryMemory
- ✅ PACT preserves emotional nuance, summary loses it
- ✅ PACT uses smart consolidation, summary is aggressive
- ✅ PACT provides graph structure, summary is just text

### vs. ConversationKGMemory (Knowledge Graph)
- ✅ PACT includes emotional edges, KG doesn't
- ✅ PACT has built-in consolidation, KG doesn't
- ✅ PACT is a managed service, KG requires manual setup

---

## Pricing

| Plan | Price | Storage | Features |
|------|-------|---------|----------|
| **Free** | $0 | 10K tokens/month | Basic memory, public data |
| **Starter** | $20/mo | 100K tokens | Emotional tracking |
| **Pro** | $99/mo | 1M tokens | Full features, analytics |
| **Team** | $299/mo | Unlimited | Shared context, priority support |

**All plans include:**
- Unlimited API calls
- Context consolidation
- 99.9% uptime SLA
- SOC 2 compliance

[View detailed pricing →](https://neurobloom.ai/pricing)

---

## Examples

### Basic Chatbot
```python
# examples/basic_usage.py
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from pact_langchain import PACTMemory

memory = PACTMemory(api_key="sk_test_...")
llm = OpenAI(temperature=0.7)
conversation = ConversationChain(llm=llm, memory=memory)

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    
    response = conversation.predict(input=user_input)
    print(f"Bot: {response}")
    
    # Show emotional state
    state = memory.get_emotional_state()
    print(f"[Emotion: {state['current_emotion']}]")
```

### Therapy/Coaching Bot
See [examples/emotional_tracking_complete.py](./examples/emotional_tracking_complete.py)

### Customer Support Agent
See [examples/support_agent.py](./examples/support_agent.py)

---

## Documentation

- [Full API Reference](https://docs.neurobloom.ai/pact/langchain/api)
- [Integration Guide](https://docs.neurobloom.ai/pact/langchain/guide)
- [Best Practices](https://docs.neurobloom.ai/pact/langchain/best-practices)
- [Migration from Standard Memory](https://docs.neurobloom.ai/pact/langchain/migration)

---

## How It Works

```
┌─────────────────┐
│  Your LangChain │
│      Agent      │
└────────┬────────┘
         │
         │ save_context() / load_memory_variables()
         │
┌────────▼────────┐
│  PACT Memory    │  ← Drop-in replacement
│  (This Package) │
└────────┬────────┘
         │
         │ API calls (REST)
         │
┌────────▼────────┐
│   PACT Server   │  ← Managed service by NeurobloomAI
│                 │  ← Handles emotional analysis
│                 │  ← Context consolidation
│                 │  ← Graph storage
└─────────────────┘
```

**Under the hood:**
1. Your agent calls `memory.save_context()` like normal
2. PACT extracts emotional signals from the text
3. PACT builds a context graph (topics, relationships, emotions)
4. PACT consolidates old context when threshold is hit
5. Your agent calls `memory.load_memory_variables()`
6. PACT returns optimized context + emotional metadata

---

## FAQ

### Q: Does this work with existing LangChain code?
**A:** Yes! It's a drop-in replacement for `ConversationBufferMemory`. Just change the import.

### Q: Do I need to change my prompts?
**A:** No. The emotional context is added as separate variables. Your prompts work as-is, but you can optionally reference `{emotional_state}` if you want.

### Q: How much does it cost?
**A:** Free tier: 10K tokens/month. Paid plans start at $20/month. [See pricing →](https://neurobloom.ai/pricing)

### Q: Where is my data stored?
**A:** On PACT's secure servers (SOC 2 compliant). You can also self-host the PACT server.

### Q: Can I use this offline?
**A:** Not yet, but self-hosted version is coming in Q2 2026.

### Q: Does it work with LangChain agents?
**A:** Yes! Works with chains, agents, and any LangChain component that uses memory.

### Q: What about privacy?
**A:** All data is encrypted in transit and at rest. You can delete sessions anytime. See [Privacy Policy](https://neurobloom.ai/privacy).

### Q: Can I visualize the memory graph?
**A:** Yes! Use `memory.get_context_graph()` to export, or use [PACT Studio](https://studio.neurobloom.ai) for a visual UI.

---

## Roadmap

- [x] Core memory integration
- [x] Emotional tracking
- [x] Context consolidation
- [x] Async support
- [ ] Self-hosted option (Q2 2026)
- [ ] Multi-session support (Q2 2026)
- [ ] LangSmith integration (Q3 2026)
- [ ] Voice tone analysis (Q3 2026)

[View full roadmap →](https://github.com/neurobloomai/pact-hx/projects/1)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md)

**Quick start:**
```bash
git clone https://github.com/neurobloomai/pact-hx.git
cd pact-hx/packages/langchain
pip install -e ".[dev]"
pytest
```

---

## Support

- 📚 [Documentation](https://docs.neurobloom.ai/pact/langchain)
- 💬 [Discord Community](https://discord.gg/neurobloom)
- 🐛 [Issue Tracker](https://github.com/neurobloomai/pact-hx/issues)
- 📧 [Email Support](mailto:hello@neurobloom.ai)

---

## License

MIT License - see [LICENSE](./LICENSE)

---

## Acknowledgments

Built with ❤️ for the LangChain community by NeurobloomAI.

Special thanks to:
- LangChain team for the amazing framework
- Early beta testers who provided feedback
- Contributors who made this possible

---

## Star History

If you find this useful, give us a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=neurobloomai/pact-hx&type=Date)](https://star-history.com/#neurobloomai/pact-hx&Date)

---

<div align="center">

**Made with 🧠 by NeurobloomAI**

[Website](https://neurobloom.ai) • [Docs](https://docs.neurobloom.ai) • [Discord](https://discord.gg/neurobloom) • [Twitter](https://twitter.com/neurobloomai)

</div>
