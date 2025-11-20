"""
LangChain VectorStore wrapper for VolcEngine RDS for MySQL native vector index.

This package provides a compatible wrapper for VolcEngine RDS for MySQL 8.0.43_20251015+ with native VECTOR(N)
columns and HNSW vector index, usable directly in LangChain for ANN/KNN similarity search.

Exports:
- VolcMySQLVectorStore: main class extending langchain_core.vectorstores.VectorStore
- MySQLVectorDistance: enum supporting 'l2' | 'euclidean' | 'cosine' distance metrics
"""

from .vectorstore import VolcMySQLVectorStore, MySQLVectorDistance

__all__ = ["VolcMySQLVectorStore", "MySQLVectorDistance"]
