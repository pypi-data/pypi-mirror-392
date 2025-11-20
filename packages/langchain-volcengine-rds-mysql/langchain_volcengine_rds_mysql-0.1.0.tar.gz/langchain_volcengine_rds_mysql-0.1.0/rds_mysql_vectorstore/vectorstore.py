import json
import uuid
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import urlparse

import pymysql

try:
    from langchain_core.vectorstores import VectorStore
except Exception:  # pragma: no cover
    # Compatible with legacy langchain versions
    from langchain.vectorstores.base import VectorStore  # type: ignore

try:
    from langchain_core.documents import Document
except Exception:  # pragma: no cover
    try:
        from langchain.schema import Document  # type: ignore
    except Exception:
        Document = Any  # type: ignore

try:
    from langchain_core.embeddings import Embeddings
except Exception:  # pragma: no cover
    try:
        from langchain.embeddings.base import Embeddings  # type: ignore
    except Exception:
        Embeddings = Any  # type: ignore


class MySQLVectorDistance(Enum):
    """Distance metric enumeration for VolcEngine RDS for MySQL vector index.

    - l2: L2 (Euclidean) distance, SQL function L2_DISTANCE
    - euclidean: Euclidean distance, SQL function EUCLIDEAN_DISTANCE
    - cosine: Cosine distance, SQL function COSINE_DISTANCE
    """

    L2 = "l2"
    EUCLIDEAN = "euclidean"
    COSINE = "cosine"

    @property
    def sql_function(self) -> str:
        if self is MySQLVectorDistance.COSINE:
            return "COSINE_DISTANCE"
        if self is MySQLVectorDistance.EUCLIDEAN:
            return "EUCLIDEAN_DISTANCE"
        return "L2_DISTANCE"


@dataclass
class _ConnParams:
    host: str
    port: int
    user: str
    password: str
    database: str


class VolcMySQLVectorStore(VectorStore):
    """LangChain-compatible VectorStore for VolcEngine RDS for MySQL native vector index.

    Key points (aligned with the official manual):
    - Vector column type: VECTOR(N)
    - Vector index: VECTOR INDEX (embedding); either USING HNSW or
      SECONDARY_ENGINE_ATTRIBUTE='{"algorithm":"hnsw","M":"16","distance":"l2"}'
    - Distance functions used for ordering: L2_DISTANCE/EUCLIDEAN_DISTANCE/COSINE_DISTANCE
    - Insert vectors via TO_VECTOR('[1,2,3]'); optional normalization VECTOR_NORMALIZE(column)
      (note: the document has a typo "vecotor_normalize"; the actual function is VECTOR_NORMALIZE)
    - ANN search must include ORDER BY dist_expr LIMIT k; optional FORCE INDEX(index_name)
    - Only InnoDB is supported; one vector index per table; index must be created on an empty
      table or at table creation time.

    This class provides: connection management, schema management (table + index), data add/delete,
    similarity search, index info, and session knob configuration.
    """

    def __init__(
        self,
        connection_uri: Optional[str] = None,
        *,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        table_name: str = "docs",
        vector_column: str = "embedding",
        index_name: Optional[str] = None,
        distance: Union[MySQLVectorDistance, str] = MySQLVectorDistance.EUCLIDEAN,
        embedding_dim: Optional[int] = None,
        embedding_function: Optional[Embeddings] = None,
        validate_server: bool = False,
    ) -> None:
        # Parse connection params and establish connection
        params = self._parse_connection_params(
            connection_uri=connection_uri,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        self._conn = pymysql.connect(
            host=params.host,
            port=params.port,
            user=params.user,
            password=params.password,
            database=params.database,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self._database = params.database

        # Schema configuration
        self.table_name = table_name
        self.vector_column = vector_column
        self.index_name = index_name or vector_column
        self.embedding_dim = embedding_dim

        # Distance metric
        if isinstance(distance, str):
            try:
                self.distance = MySQLVectorDistance(distance.lower())
            except Exception:
                raise ValueError(
                    "distance must be one of 'l2'|'euclidean'|'cosine'"
                )
        else:
            self.distance = distance

        # Optional embedding function
        self._embedding_function = embedding_function

        # Optional validation: server version and knob
        if validate_server:
            self._validate_server()

    # ------------------------------
    # Connection helpers
    # ------------------------------

    @staticmethod
    def _parse_connection_params(
        connection_uri: Optional[str],
        host: Optional[str],
        port: Optional[int],
        user: Optional[str],
        password: Optional[str],
        database: Optional[str],
    ) -> _ConnParams:
        """Parse connection parameters.

        Supports:
        - connection_uri: mysql+pymysql://user:pass@host:port/db
        - discrete params: host/port/user/password/database
        """
        if connection_uri:
            parsed = urlparse(connection_uri)
            if parsed.scheme not in {"mysql+pymysql", "mysql"}:
                raise ValueError("Connection URI must start with 'mysql+pymysql://' or 'mysql://'")
            if not parsed.hostname or not parsed.path or parsed.path == "/":
                raise ValueError("URI must include host and database name")
            return _ConnParams(
                host=parsed.hostname,
                port=parsed.port or 3306,
                user=(parsed.username or ""),
                password=(parsed.password or ""),
                database=parsed.path.lstrip("/"),
            )
        # Use discrete params
        if not (host and user and password and database):
            raise ValueError(
                "Must provide connection_uri or (host, user, password, database)"
            )
        return _ConnParams(
            host=host,
            port=port or 3306,
            user=user,
            password=password,
            database=database,
        )

    def _cursor(self):
        return self._conn.cursor()

    def _validate_server(self) -> None:
        """Validate MySQL version and vector index knob.

        Requirement: MySQL 8.0.43_20251015+, and loose_vector_index_enabled=ON.
        Version parsing is based on VERSION() major/minor/patch; patch must be >= 43.
        """
        with self._cursor() as cur:
            cur.execute("SELECT VERSION() AS v")
            row = cur.fetchone() or {}
            ver = str(row.get("v", ""))
            try:
                # e.g., 8.0.43_20251015-log
                main = ver.split("-")[0]
                base = main.split("_")[0]
                parts = base.split(".")
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                if not (major == 8 and minor == 0 and patch >= 43):
                    raise ValueError
            except Exception:
                raise RuntimeError(
                    f"Unsupported MySQL version: {ver}, requires >= 8.0.43_20251015"
                )
            # Check knob
            cur.execute(
                "SHOW VARIABLES LIKE 'loose_vector_index_enabled'"
            )
            row2 = cur.fetchone() or {}
            if str(row2.get("Value", "")).upper() != "ON":
                raise RuntimeError(
                    "loose_vector_index_enabled is OFF; please enable this parameter on the instance"
                )

    @staticmethod
    def _quote_ident(name: str) -> str:
        """Safely quote identifier; allow only letters, digits and underscore to avoid injection."""
        if not name or not name.replace("_", "").isalnum():
            raise ValueError(f"Invalid identifier: {name}")
        return f"`{name}`"

    @staticmethod
    def _embedding_to_str(vec: List[float], expect_dim: Optional[int]) -> str:
        if expect_dim is not None and len(vec) != expect_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {expect_dim}, got {len(vec)}"
            )
        # Use JSON string as input for TO_VECTOR, e.g., "[1.0,2.0,3.0]"
        return json.dumps(vec, ensure_ascii=False, separators=(",", ":"))

    # ------------------------------
    # Schema management
    # ------------------------------

    def create_schema(
        self,
        table_name: Optional[str],
        embedding_dim: int,
        algorithm_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a table with a vector column and vector index (InnoDB only).

        Note: per the RDS manual, the vector index must be created on an empty table or
        at table creation time; you cannot add a vector index to a table with existing data.

        DDL template:
        CREATE TABLE IF NOT EXISTS {table} (
          id VARCHAR(64) PRIMARY KEY,
          content TEXT,
          metadata JSON,
          embedding VECTOR({dim}) NOT NULL,
          VECTOR INDEX (embedding)
          [USING HNSW]
          [SECONDARY_ENGINE_ATTRIBUTE='{"algorithm":"hnsw","M":"16","distance":"l2"}']
        ) ENGINE=InnoDB;
        """
        if table_name:
            self.table_name = table_name
        self.embedding_dim = embedding_dim

        vec_idx_clause = "VECTOR INDEX (embedding)"
        using_clause = ""
        secondary_attr_clause = ""
        ap = algorithm_params or {}

        # Support USING HNSW
        using = ap.get("using") or ap.get("algorithm")
        if using and str(using).lower() == "hnsw":
            using_clause = " USING HNSW"

        # SECONDARY_ENGINE_ATTRIBUTE JSON
        # Accept top-level 'distance', 'M', 'ef_construction', and nested 'secondary_engine_attribute'
        sea = ap.get("secondary_engine_attribute") or {}
        sea = dict(sea)  # copy
        # Fill top-level params
        if ap.get("distance") and "distance" not in sea:
            sea["distance"] = str(ap.get("distance")).lower()
        if ap.get("M") and "M" not in sea:
            sea["M"] = str(ap.get("M"))
        if ap.get("ef_construction") and "ef_construction" not in sea:
            sea["ef_construction"] = str(ap.get("ef_construction"))
        if using_clause or sea:
            # Default algorithm: hnsw
            if "algorithm" not in sea:
                sea["algorithm"] = "hnsw"
            # Generate JSON string
            sea_json = json.dumps(sea, ensure_ascii=False, separators=(",", ":"))
            secondary_attr_clause = f" SECONDARY_ENGINE_ATTRIBUTE='{sea_json}'"

        ddl = (
            f"CREATE TABLE IF NOT EXISTS {self._quote_ident(self.table_name)} (\n"
            "  id VARCHAR(64) PRIMARY KEY,\n"
            "  content TEXT,\n"
            "  metadata JSON,\n"
            f"  embedding VECTOR({int(self.embedding_dim)}) NOT NULL,\n"
            f"  {vec_idx_clause}{using_clause}{secondary_attr_clause}\n"
            ") ENGINE=InnoDB;"
        )

        with self._cursor() as cur:
            cur.execute(ddl)

    def drop_index(self, index_name: Optional[str] = None) -> None:
        idx = index_name or self.index_name
        sql = (
            f"DROP INDEX {self._quote_ident(idx)} ON {self._quote_ident(self.table_name)}"
        )
        with self._cursor() as cur:
            cur.execute(sql)

    def drop_table(self, table_name: Optional[str] = None) -> None:
        tbl = self._quote_ident(table_name or self.table_name)
        with self._cursor() as cur:
            cur.execute(f"DROP TABLE {tbl}")

    def get_index_info(self, index_name: Optional[str] = None) -> Optional[str]:
        idx = index_name or self.index_name
        with self._cursor() as cur:
            cur.execute(
                "SELECT VECTOR_INDEX_INFO(%s,%s,%s) AS info",
                (self._database, self.table_name, idx),
            )
            row = cur.fetchone() or {}
            return row.get("info")

    def configure_session(
        self,
        loose_default_vector_distance: Optional[str] = None,
        loose_hnsw_ef_search: Optional[int] = None,
    ) -> None:
        """Configure session-level vector index knobs.

        - loose_default_vector_distance: 'euclidean'|'l2'|'cosine'
        - loose_hnsw_ef_search: 1..10000 (candidate width; larger => higher recall, more cost)
        """
        clauses: List[str] = []
        if loose_default_vector_distance:
            v = str(loose_default_vector_distance).lower()
            if v not in {"euclidean", "l2", "cosine"}:
                raise ValueError("Invalid value for loose_default_vector_distance")
            clauses.append(f"loose_default_vector_distance = '{v}'")
        if loose_hnsw_ef_search is not None:
            ef = int(loose_hnsw_ef_search)
            if not (1 <= ef <= 10000):
                raise ValueError("loose_hnsw_ef_search must be in [1, 10000]")
            clauses.append(f"loose_hnsw_ef_search = {ef}")
        if not clauses:
            return
        sql = "SET SESSION " + ", ".join(clauses)
        with self._cursor() as cur:
            cur.execute(sql)

    # ------------------------------
    # Data add/delete
    # ------------------------------

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[Iterable[Dict[str, Any]]] = None,
        ids: Optional[Iterable[str]] = None,
        embeddings: Optional[Iterable[List[float]]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Insert texts with precomputed embeddings or via an external Embeddings model.

        MySQL does NOT perform text-to-vector conversion. You must compute embeddings externally
        before insertion. If ``embeddings`` are not provided, an ``embedding_function`` must be
        configured in this store and will be used to call ``embed_documents(texts)`` externally.

        Vectors are inserted with ``TO_VECTOR(json_str)``. The embedding dimension is validated
        (and auto-set on first use if ``self.embedding_dim`` is None).
        """
        texts_list = list(texts)
        metas_list = list(metadatas or [{} for _ in texts_list])
        ids_list = list(ids or [])
        if ids_list:
            if len(ids_list) != len(texts_list):
                raise ValueError("Length of ids must match length of texts")
        else:
            ids_list = [uuid.uuid4().hex for _ in texts_list]

        if embeddings is None:
            if self._embedding_function is None:
                raise ValueError(
                    "Embeddings not provided and instance has no embedding_function configured"
                )
            vectors = self._embedding_function.embed_documents(texts_list)
        else:
            vectors = list(embeddings)

        if len(vectors) != len(texts_list):
            raise ValueError("Number of embeddings must match number of texts")
        if self.embedding_dim is None:
            # Auto-detect dimension on first use
            self.embedding_dim = len(vectors[0])

        sql = (
            f"INSERT INTO {self._quote_ident(self.table_name)} (id, content, metadata, {self._quote_ident(self.vector_column)}) "
            "VALUES (%s, %s, %s, TO_VECTOR(%s))"
        )
        with self._cursor() as cur:
            for i, text in enumerate(texts_list):
                meta = metas_list[i] if i < len(metas_list) else {}
                vec = vectors[i]
                vec_str = self._embedding_to_str(vec, self.embedding_dim)
                meta_str = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
                cur.execute(sql, (ids_list[i], text, meta_str, vec_str))
        return ids_list

    def add_documents(
        self,
        documents: Iterable[Document],
        ids: Optional[Iterable[str]] = None,
        embeddings: Optional[Iterable[List[float]]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Insert Document objects using precomputed vectors or an external Embeddings model.

        MySQL does NOT embed text. You must compute embeddings externally before insertion.
        If ``embeddings`` are not provided, an ``embedding_function`` must be configured in this store
        and will be used to call ``embed_documents([d.page_content ...])`` externally.
        """
        texts = [d.page_content for d in documents]
        metas = [getattr(d, "metadata", {}) or {} for d in documents]
        return self.add_texts(texts, metadatas=metas, ids=ids, embeddings=embeddings)

    def add_embeddings(
        self,
        vectors: Iterable[List[float]],
        texts: Optional[Iterable[str]] = None,
        metadatas: Optional[Iterable[Dict[str, Any]]] = None,
        ids: Optional[Iterable[str]] = None,
    ) -> List[str]:
        """Insert rows using provided precomputed vectors.

        MySQL does NOT embed text; embeddings must be computed externally before storage.
        If ``texts`` is None, an empty string is stored in ``content``. The embedding dimension is
        validated (and auto-set on first use if ``self.embedding_dim`` is None). Vectors are inserted
        via ``TO_VECTOR(json_str)``.
        """
        vecs_list = list(vectors)
        texts_list = list(texts or ["" for _ in vecs_list])
        metas_list = list(metadatas or [{} for _ in vecs_list])
        ids_list = list(ids or [])

        if ids_list:
            if len(ids_list) != len(vecs_list):
                raise ValueError("Length of ids must match number of vectors")
        else:
            ids_list = [uuid.uuid4().hex for _ in vecs_list]

        if texts is not None and len(texts_list) != len(vecs_list):
            raise ValueError("Length of texts must match number of vectors")

        if self.embedding_dim is None:
            if not vecs_list:
                return ids_list
            self.embedding_dim = len(vecs_list[0])

        sql = (
            f"INSERT INTO {self._quote_ident(self.table_name)} (id, content, metadata, {self._quote_ident(self.vector_column)}) "
            "VALUES (%s, %s, %s, TO_VECTOR(%s))"
        )
        with self._cursor() as cur:
            for i, vec in enumerate(vecs_list):
                text = texts_list[i] if i < len(texts_list) else ""
                meta = metas_list[i] if i < len(metas_list) else {}
                vec_str = self._embedding_to_str(vec, self.embedding_dim)
                meta_str = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
                cur.execute(sql, (ids_list[i], text, meta_str, vec_str))
        return ids_list

    def delete(self, ids: List[str], **kwargs: Any) -> bool:
        if not ids:
            return True
        placeholders = ",".join(["%s"] * len(ids))
        sql = (
            f"DELETE FROM {self._quote_ident(self.table_name)} WHERE id IN ({placeholders})"
        )
        with self._cursor() as cur:
            cur.execute(sql, list(ids))
        return True

    # ------------------------------
    # Search
    # ------------------------------

    def _build_where_clause(
        self, filter: Optional[Union[str, Dict[str, Any]]]
    ) -> Tuple[str, List[Any]]:
        if filter is None:
            return "", []
        if isinstance(filter, str):
            # Use as-is in WHERE (ensure safety yourself if building dynamically)
            return f" WHERE {filter} ", []
        # Simple metadata filter: equality via JSON_EXTRACT
        parts: List[str] = []
        args: List[Any] = []
        for k, v in filter.items():
            path = f"$.{k}"
            # Compare as string via JSON_UNQUOTE(JSON_EXTRACT(...)) for uniformity
            parts.append("JSON_UNQUOTE(JSON_EXTRACT(metadata, %s)) = %s")
            args.extend([path, str(v)])
        if parts:
            return " WHERE " + " AND ".join(parts) + " ", args
        return "", []

    def _dist_expr(self, normalize: bool) -> str:
        col = self._quote_ident(self.vector_column)
        col_expr = f"VECTOR_NORMALIZE({col})" if normalize else col
        func = self.distance.sql_function
        return f"{func}({col_expr}, TO_VECTOR(%s))"

    def _query_base_sql(
        self,
        force_index: bool,
        where_clause: str,
        dist_expr: str,
    ) -> str:
        tbl = self._quote_ident(self.table_name)
        idx = self._quote_ident(self.index_name)
        force = f" FORCE INDEX({idx})" if force_index else ""
        # Return dist in SELECT list to support with_score
        sql = (
            f"SELECT id, content, metadata, {dist_expr} AS dist "
            f"FROM {tbl}{force}{where_clause}"
            f" ORDER BY dist LIMIT %s"
        )
        return sql

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        *,
        filter: Optional[Union[str, Dict[str, Any]]] = None,
        normalize: bool = False,
        force_index: bool = True,
        **kwargs: Any,
    ) -> List[Document]:
        """Similarity search using a text query.

        MySQL does NOT perform text-to-vector conversion. You must use an external Embeddings model
        to compute the query vector. This method requires that an ``embedding_function`` is configured
        in the store; otherwise, compute the query vector externally and call
        :meth:`similarity_search_by_vector`.
        """
        if self._embedding_function is None:
            raise ValueError("Embedding function not configured; cannot embed query text")
        qvec = self._embedding_function.embed_query(query)
        return self.similarity_search_by_vector(
            qvec, k, filter=filter, normalize=normalize, force_index=force_index
        )

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        *,
        filter: Optional[Union[str, Dict[str, Any]]] = None,
        normalize: bool = False,
        force_index: bool = True,
        **kwargs: Any,
    ) -> List[Document]:
        """Similarity search given a precomputed query vector.

        MySQL does NOT embed text. Provide an externally computed vector for the query. The vector is
        passed via ``TO_VECTOR(json_str)``; the embedding dimension is validated and auto-set on first
        use if needed.
        """
        if self.embedding_dim is None:
            self.embedding_dim = len(embedding)
        vec_str = self._embedding_to_str(embedding, self.embedding_dim)
        where_clause, args = self._build_where_clause(filter)
        dist_expr = self._dist_expr(normalize=normalize)
        sql = self._query_base_sql(force_index=force_index, where_clause=where_clause, dist_expr=dist_expr)
        params = args + [vec_str, int(k)]
        docs: List[Document] = []
        with self._cursor() as cur:
            cur.execute(sql, params)
            for row in cur.fetchall() or []:
                meta_raw = row.get("metadata")
                try:
                    meta = json.loads(meta_raw) if isinstance(meta_raw, str) else (meta_raw or {})
                except Exception:
                    meta = {"_metadata_raw": meta_raw}
                # Attach distance into metadata for convenience
                meta = dict(meta or {})
                meta["distance"] = float(row.get("dist", 0.0))
                docs.append(Document(page_content=row.get("content") or "", metadata=meta))
        return docs

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        *,
        filter: Optional[Union[str, Dict[str, Any]]] = None,
        normalize: bool = False,
        force_index: bool = True,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        if self._embedding_function is None:
            raise ValueError("Embedding function not configured; cannot embed query text")
        qvec = self._embedding_function.embed_query(query)
        return self.similarity_search_by_vector_with_score(
            qvec, k, filter=filter, normalize=normalize, force_index=force_index
        )

    def similarity_search_by_vector_with_score(
        self,
        embedding: List[float],
        k: int = 4,
        *,
        filter: Optional[Union[str, Dict[str, Any]]] = None,
        normalize: bool = False,
        force_index: bool = True,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        if self.embedding_dim is None:
            self.embedding_dim = len(embedding)
        vec_str = self._embedding_to_str(embedding, self.embedding_dim)
        where_clause, args = self._build_where_clause(filter)
        dist_expr = self._dist_expr(normalize=normalize)
        sql = self._query_base_sql(force_index=force_index, where_clause=where_clause, dist_expr=dist_expr)
        params = args + [vec_str, int(k)]
        results: List[Tuple[Document, float]] = []
        with self._cursor() as cur:
            cur.execute(sql, params)
            for row in cur.fetchall() or []:
                meta_raw = row.get("metadata")
                try:
                    meta = json.loads(meta_raw) if isinstance(meta_raw, str) else (meta_raw or {})
                except Exception:
                    meta = {"_metadata_raw": meta_raw}
                doc = Document(page_content=row.get("content") or "", metadata=meta)
                score = float(row.get("dist", 0.0))
                results.append((doc, score))
        return results

    # ------------------------------
    # Convenience constructors
    # ------------------------------

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        *,
        connection_uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        table_name: str = "docs",
        algorithm_params: Optional[Dict[str, Any]] = None,
        distance: Union[MySQLVectorDistance, str] = MySQLVectorDistance.EUCLIDEAN,
        normalize: bool = False,
    ) -> "VolcMySQLVectorStore":
        """Build and populate a table from texts and an Embeddings instance; returns a VectorStore.
        Creates the table if it does not exist.
        """
        vectors = embedding.embed_documents(texts)
        if not vectors:
            raise ValueError("embed_documents returned empty")
        dim = len(vectors[0])
        vs = cls(
            connection_uri=connection_uri,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            table_name=table_name,
            embedding_dim=dim,
            embedding_function=embedding,
            distance=distance,
        )
        # Attempt to create table (IF NOT EXISTS); index can only be created on empty table or at creation
        vs.create_schema(table_name, dim, algorithm_params=algorithm_params)
        vs.add_texts(texts=texts, embeddings=vectors)
        return vs

    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding: Embeddings,
        *,
        connection_uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        table_name: str = "docs",
        algorithm_params: Optional[Dict[str, Any]] = None,
        distance: Union[MySQLVectorDistance, str] = MySQLVectorDistance.EUCLIDEAN,
        normalize: bool = False,
    ) -> "VolcMySQLVectorStore":
        texts = [d.page_content for d in documents]
        vectors = embedding.embed_documents(texts)
        if not vectors:
            raise ValueError("embed_documents returned empty")
        dim = len(vectors[0])
        vs = cls(
            connection_uri=connection_uri,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            table_name=table_name,
            embedding_dim=dim,
            embedding_function=embedding,
            distance=distance,
        )
        vs.create_schema(table_name, dim, algorithm_params=algorithm_params)
        vs.add_documents(documents=documents, embeddings=vectors)
        return vs

    @classmethod
    def from_vectors(
        cls,
        vectors: List[List[float]],
        *,
        texts: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        connection_uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        table_name: str = "docs",
        algorithm_params: Optional[Dict[str, Any]] = None,
        distance: Union[MySQLVectorDistance, str] = MySQLVectorDistance.EUCLIDEAN,
    ) -> "VolcMySQLVectorStore":
        """Construct a store from externally precomputed vectors and optional texts/metadata.

        Creates schema with ``dim = len(vectors[0])`` and populates it via :meth:`add_embeddings`.
        No Embeddings object is used; this assumes you computed vectors externally.
        """
        if not vectors:
            raise ValueError("vectors must not be empty")
        dim = len(vectors[0])
        vs = cls(
            connection_uri=connection_uri,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            table_name=table_name,
            embedding_dim=dim,
            embedding_function=None,
            distance=distance,
        )
        vs.create_schema(table_name, dim, algorithm_params=algorithm_params)
        vs.add_embeddings(vectors=vectors, texts=texts, metadatas=metadatas)
        return vs
