"""Setup configuration for pact-langchain package."""

from setuptools import setup, find_packages
import os

# Read README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "LangChain memory with emotional intelligence by NeurobloomAI"

setup(
    name="pact-langchain",
    version="0.1.0",
    author="NeurobloomAI",
    author_email="hello@neurobloom.ai",
    description="LangChain memory with emotional intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neurobloomai/pact-hx",
    project_urls={
        "Bug Reports": "https://github.com/neurobloomai/pact-hx/issues",
        "Source": "https://github.com/neurobloomai/pact-hx",
        "Documentation": "https://docs.neurobloom.ai/pact/langchain",
        "Homepage": "https://neurobloom.ai",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "langchain-community>=0.0.10",  # Added for LangChain compatibility
        "requests>=2.28.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
        "examples": [
            "langchain-openai>=0.0.5",  # For running examples
            "python-dotenv>=1.0.0",
        ],
    },
    keywords="langchain memory ai llm emotional-intelligence context pact neurobloom",
)
