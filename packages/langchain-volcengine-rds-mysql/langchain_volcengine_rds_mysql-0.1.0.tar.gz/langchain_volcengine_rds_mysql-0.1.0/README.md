# VolcEngine RDS for MySQL VectorStore for LangChain

This package provides a LangChain-compatible `VectorStore` for [VolcEngine RDS for MySQL](https://www.volcengine.com/product/rds-mysql), leveraging its native vector indexing and Approximate Nearest Neighbor (ANN) search capabilities. It allows you to use a fully managed, high-performance relational database as a vector store directly within your LangChain applications.

The integration is built upon the native `VECTOR(N)` data type and HNSW-based vector indexing introduced in MySQL `8.0.43_20251015`, enabling efficient similarity searches without external services or plugins.

## Overview

[VolcEngine (Volcano Engine)](https://www.volcengine.com) is the public cloud platform from ByteDance, offering a wide range of cloud computing services. **VolcEngine RDS for MySQL** is its fully managed relational database service, providing robust performance, high availability, and scalability.

This vector store integration brings the power of native vector search to your MySQL database, featuring:
- **Native Integration**: Uses MySQL's built-in `VECTOR(N)` columns, `VECTOR INDEX`, and distance functions (`L2_DISTANCE`, `EUCLIDEAN_DISTANCE`, `COSINE_DISTANCE`).
- **HNSW Indexing**: Leverages the efficient Hierarchical Navigable Small World (HNSW) algorithm for fast ANN searches.
- **LangChain Compatibility**: Extends `langchain_core.vectorstores.VectorStore` to support standard methods like `add_texts`, `similarity_search`, and `from_texts`.
- **Simple and Flexible**: Offers straightforward connection via standard PyMySQL URIs or parameters and includes helpers for schema and index management.

## Before you begin

To get started, you will need to complete the following steps:

1.  **Create a VolcEngine Account**: If you don't have one, [sign up for a VolcEngine account](https://www.volcengine.com/docs/6291/65511) and create a project.
2.  **Create a VolcEngine RDS for MySQL Instance**: Provision a new RDS for MySQL instance. The instance version **must be 8.0.43_20251015 or higher** to support native vector functions.
3.  **Enable Vector Indexing**: In the instance's parameter settings, find and set the `loose_vector_index_enabled` parameter to `ON`. This is required to execute any DDL or queries related to vector indexes.
4.  **Create a Database and User**: Create a new database within your instance and a user account with sufficient privileges to connect and manage tables.
5.  **Ensure Network Access**: Configure network access to your instance, either by enabling a public IP address or by setting up a VPC and ensuring your application's environment can connect to it.

## Install

This package requires Python 3.9 or higher. Install the necessary libraries using pip:

```bash
pip install langchain-core langchain-community pymysql typing-extensions
```

You can install this integration package from PyPI:

```bash
pip install langchain-volcengine-rds-mysql
```

Note: The Python import path remains unchanged. After installation, import the classes as:

```python
from rds_mysql_vectorstore import VolcMySQLVectorStore, MySQLVectorDistance
```


## Authentication and Connection

Connection to your VolcEngine RDS for MySQL instance is handled via the standard `pymysql` library. You can provide connection details either as a single database URI or as discrete parameters.

```python
from rds_mysql_vectorstore import VolcMySQLVectorStore

# Option 1: Using a connection URI (recommended)
DB_URI = "mysql+pymysql://user:password@your_instance_host:3306/your_database"
store = VolcMySQLVectorStore(connection_uri=DB_URI, table_name="my_documents")

# Option 2: Using discrete parameters
store = VolcMySQLVectorStore(
    host="your_instance_host",
    port=3306,
    user="user",
    password="password",
    database="your_database",
    table_name="my_documents",
)
```

## Basic Usage

The typical workflow involves initializing the database schema, creating an embeddings model, populating the vector store, and performing searches.

### Set Database Values

First, define the connection parameters for your database.

```python
DB_HOST = "your_instance_host"
DB_PORT = 3306
DB_USER = "user"
DB_PASSWORD = "password"
DB_DATABASE = "your_database"
TABLE_NAME = "docs_table"
```

### Initialize Table with Vector Index

Before adding data, you must create a table with the correct schema, including a `VECTOR` column and a vector index. The `create_schema` method handles this.

**Important**: A vector index can only be created on an empty table or at the time of table creation.

```python
from rds_mysql_vectorstore import VolcMySQLVectorStore

# Initialize the store first (without data)
store = VolcMySQLVectorStore(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_DATABASE,
    table_name=TABLE_NAME,
)

# Define vector size and index parameters
VECTOR_SIZE = 4  # Example dimension
algorithm_params = {
    "distance": "l2",   # L2/EUCLIDEAN/COSINE supported
    "M": 16,
    "ef_construction": 100,
}

# Create the table and HNSW index
store.create_schema(
    table_name=TABLE_NAME,
    vector_size=VECTOR_SIZE,
    algorithm_params=algorithm_params
)
```

### Create an Embeddings Model

VolcEngine RDS for MySQL does not generate embeddings from text. You must use a LangChain-compatible embeddings model to compute vectors for your documents and queries externally.

```python
from langchain_community.embeddings import FakeEmbeddings

# Use any LangChain embeddings model
embedder = FakeEmbeddings(size=VECTOR_SIZE)
```

### Initialize the VectorStore

You can initialize the `VolcMySQLVectorStore` by providing connection details and the table name. If you plan to use methods like `similarity_search` (which take text queries), you must also provide an `embedding_function`.

```python
store = VolcMySQLVectorStore(
    host=DB_HOST,
    # ... other connection params
    database=DB_DATABASE,
    table_name=TABLE_NAME,
    embedding_function=embedder, # Needed for text-based searches
)
```

### Add Texts

You can add documents to the store using `add_texts`. If you have already computed the embeddings, you can pass them directly to avoid re-computation.

```python
texts = [
    "Apples are a type of fruit",
    "Bananas are a yellow fruit",
    "Cars are a type of vehicle",
]

# The store will use its configured embedder to compute vectors
store.add_texts(texts)
```

### Delete Texts by IDs

You can remove documents from the store by providing a list of their IDs.

```python
# Assuming you have the IDs from the add_texts return value
ids_to_delete = ["some-uuid-1", "some-uuid-2"]
store.delete(ids_to_delete)
```

### Search for Documents (by Text)

To search for documents similar to a text query, use `similarity_search`. This requires the `embedding_function` to be configured on the store.

```python
query = "Which fruit is yellow?"
results = store.similarity_search(query, k=1)
print(results[0].page_content)
# Expected output: "Bananas are a yellow fruit"
```

### Search by Vector

If you have a precomputed query vector, use `similarity_search_by_vector` to perform the search directly.

```python
query_vector = embedder.embed_query(query)
results = store.similarity_search_by_vector(query_vector, k=1)
print(results[0].page_content)
# Expected output: "Bananas are a yellow fruit"
```

## Index Management

The vector index is created using a Data Definition Language (DDL) statement that specifies the index type and parameters. This library abstracts this process through the `create_schema` method.

- **Index Creation**: The DDL uses `VECTOR INDEX (embedding)` with optional clauses like `USING HNSW` or `SECONDARY_ENGINE_ATTRIBUTE` to configure the HNSW algorithm (`M`, `ef_construction`) and distance metric.
- **Dropping an Index**: You can remove an index using `drop_index()`.

```python
# Drop index via wrapper
store.drop_index()  # default to vector_column name
store.drop_index("embedding_idx")

# Inspect index info via wrapper
info = store.get_index_info()
print(info)

# (Optional) Drop the table via wrapper
store.drop_table()
```


```python
# Example DDL generated by create_schema:
# CREATE TABLE IF NOT EXISTS `docs_table` (
#   id VARCHAR(64) PRIMARY KEY,
#   content TEXT,
#   metadata JSON,
#   embedding VECTOR(4) NOT NULL,
#   VECTOR INDEX (embedding) USING HNSW SECONDARY_ENGINE_ATTRIBUTE='{"distance":"l2","M":"16","ef_construction":"100","algorithm":"hnsw"}'
# ) ENGINE=InnoDB;

# To verify if the index is being used, you can use EXPLAIN on a query.
# If the "Extra" column in the output shows "Using ANN Search", the index is active.
```

## Advanced Usage

### Custom Metadata and Filtering

The default schema includes a `metadata` column of type `JSON`. You can store arbitrary key-value pairs here and use them for filtering during a search. The `filter` parameter accepts either a SQL `WHERE` clause string or a dictionary for simple equality checks.

```python
# Add texts with metadata
store.add_texts(
    ["A document about cats"],
    metadatas=[{"topic": "animals", "year": 2023}]
)

# Filter using a dictionary (creates JSON_EXTRACT equality checks)
results_dict = store.similarity_search(
    "Feline friends",
    filter={"topic": "animals", "year": "2023"}
)

# Filter using a SQL string (more flexible)
results_sql = store.similarity_search(
    "Feline friends",
    filter="JSON_EXTRACT(metadata, '$.year') > 2022"
)
```

### Session Knobs

VolcEngine RDS for MySQL allows tuning HNSW parameters at the session level. You can use `configure_session` to adjust settings like `loose_hnsw_ef_search`, which controls the size of the dynamic candidate list during a search. Higher values can improve recall at the cost of performance.

```python
# Tune ef_search for the current session
store.configure_session(loose_hnsw_ef_search=50)

# Subsequent queries in this session will use the new value
results = store.similarity_search("Which fruit is yellow?", k=5)
```

### FORCE INDEX Behavior

By default, all search queries include a `FORCE INDEX` hint to ensure the database uses the vector index for an ANN search. You can disable this by setting `force_index=False` in the search method, which allows the MySQL optimizer to decide whether to use the index or perform a full table scan (KNN).

## Important Notes

- **External Embeddings**: VolcEngine RDS for MySQL **cannot** embed text on its own. You must always compute embeddings externally using a separate model for both data ingestion and querying.
- **Vector Index Constraints**:
    - The table must use the **InnoDB** storage engine.
    - Only **one** vector index is allowed per table.
    - The vector index must be created on an **empty table** or defined at table creation. You cannot add a vector index to a table that already contains data.

## Troubleshooting

- **Unsupported MySQL Version**: If you receive an error like `Unsupported MySQL version`, ensure your instance is `8.0.43_20251015` or higher.
- **Vector Index Knob is Off**: Errors during DDL execution (`CREATE TABLE` with a vector index) often mean `loose_vector_index_enabled` is `OFF`. Enable it in your instance's parameter settings.
- **Dimension Mismatch**: An error like `Embedding dimension mismatch` means the vector's size does not match the `VECTOR(N)` column's dimension. Ensure your embeddings model produces vectors of the correct size.
- **`FORCE INDEX` Effects**: If queries are slow or do not return expected results, verify with `EXPLAIN` that the vector index is being used. If not, check if `force_index` was accidentally turned off.

## Code Examples

Below are two common workflows for populating and querying the vector store.

### Example A: Pre-compute vectors and search by vector

This approach is recommended for clarity and control. You compute embeddings for your documents and queries externally and use the `_by_vector` search methods.

```python
from rds_mysql_vectorstore import VolcMySQLVectorStore, MySQLVectorDistance
from langchain_community.embeddings import FakeEmbeddings

DB_URI = "mysql+pymysql://user:password@127.0.0.1:3306/test"
embedder = FakeEmbeddings(size=4)
texts = ["Apples are fruit", "Bananas are yellow fruit", "Cars are vehicles"]

# 1. Pre-compute document embeddings externally
doc_vectors = embedder.embed_documents(texts)

# 2. Create schema and insert data using precomputed vectors
store = VolcMySQLVectorStore.from_vectors(
    vectors=doc_vectors,
    texts=texts,
    connection_uri=DB_URI,
    table_name="docs_a",
    algorithm_params={"distance": "l2"},
    distance=MySQLVectorDistance.L2,
)

# 3. Compute query vector externally and search via ANN
query_vector = embedder.embed_query("Which fruit is yellow?")
results = store.similarity_search_by_vector(query_vector, k=2)

for doc in results:
    print(doc.page_content, doc.metadata.get("distance"))
```

### Example B: Provide an embeddings model for convenience

This approach uses the standard `from_texts` and `similarity_search` methods. The vector store calls your provided embeddings model under the hood to compute vectors before sending them to the database.

```python
from rds_mysql_vectorstore import VolcMySQLVectorStore, MySQLVectorDistance
from langchain_community.embeddings import FakeEmbeddings

DB_URI = "mysql+pymysql://user:password@127.0.0.1:3306/test"
embedder = FakeEmbeddings(size=4)
texts = ["Apples are fruit", "Bananas are yellow fruit", "Cars are vehicles"]

# 1. Create store from texts, providing an embedding model
store = VolcMySQLVectorStore.from_texts(
    texts=texts,
    embedding=embedder,
    connection_uri=DB_URI,
    table_name="docs_b",
    algorithm_params={"distance": "l2"},
    distance=MySQLVectorDistance.L2,
)

# 2. Similarity search by text (store handles embedding the query)
results = store.similarity_search("Which fruit is yellow?", k=2)

for doc in results:
    print(doc.page_content, doc.metadata.get("distance"))
```

## API Reference

For detailed information on all classes, methods, and parameters, please refer to the docstrings in the source code: `rds_mysql_vectorstore/vectorstore.py`.
