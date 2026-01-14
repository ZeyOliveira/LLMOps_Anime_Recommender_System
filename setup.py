from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="llmops-rag-anime-recommender",
    version="0.1.0",
    author="Zey Oliveira",
    description="End-to-end LLMOps pipeline for anime recommendation",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.12",
)
