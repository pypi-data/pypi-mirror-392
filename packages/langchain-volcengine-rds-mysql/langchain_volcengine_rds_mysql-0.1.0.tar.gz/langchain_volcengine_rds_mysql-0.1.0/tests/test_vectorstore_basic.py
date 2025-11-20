import sys
import types
import unittest
from unittest import mock

# Ensure pymysql import can succeed without external dependency
if "pymysql" not in sys.modules:
    fake_pymysql = types.SimpleNamespace()
    # Provide cursors.DictCursor placeholder used by vectorstore
    fake_pymysql.cursors = types.SimpleNamespace(DictCursor=object())
    sys.modules["pymysql"] = fake_pymysql

# Stub langchain_core modules to avoid external dependency
if "langchain_core.vectorstores" not in sys.modules:
    VectorStoreStub = type("VectorStore", (), {})
    sys.modules["langchain_core.vectorstores"] = types.SimpleNamespace(VectorStore=VectorStoreStub)
if "langchain_core.documents" not in sys.modules:
    class DocumentStub:
        def __init__(self, page_content: str, metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}
    sys.modules["langchain_core.documents"] = types.SimpleNamespace(Document=DocumentStub)

from rds_mysql_vectorstore.vectorstore import VolcMySQLVectorStore, MySQLVectorDistance


class FakeCursor:
    def __init__(self):
        self.executed = []  # list of tuples (sql, params)
        self.last_sql = None
        self.last_params = None

    def execute(self, sql, params=None):
        self.last_sql = sql
        self.last_params = params
        self.executed.append((sql, params))
        return None

    def fetchall(self):
        # Simulate empty result set
        return []

    def fetchone(self):
        # Simulate empty row
        return {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, **kwargs):
        # Capture connection kwargs for debug if needed
        self.kwargs = kwargs
        self.last_cursor = None

    def cursor(self):
        self.last_cursor = FakeCursor()
        return self.last_cursor


class VectorStoreBasicTests(unittest.TestCase):
    @mock.patch("rds_mysql_vectorstore.vectorstore.pymysql.connect", create=True)
    def test_parse_connection_uri_and_params(self, connect_mock):
        # Return a fake connection for any connect call
        connect_mock.return_value = FakeConnection()

        # URI parse case
        uri = "mysql+pymysql://user:password@127.0.0.1:3306/testdb"
        vs1 = VolcMySQLVectorStore(connection_uri=uri, table_name="t1")
        self.assertTrue(connect_mock.called)
        call1 = connect_mock.call_args_list[0]
        kwargs1 = call1.kwargs
        self.assertEqual(kwargs1.get("host"), "127.0.0.1")
        self.assertEqual(kwargs1.get("port"), 3306)
        self.assertEqual(kwargs1.get("user"), "user")
        self.assertEqual(kwargs1.get("password"), "password")
        self.assertEqual(kwargs1.get("database"), "testdb")
        # Ensure DictCursor passed
        self.assertIn("cursorclass", kwargs1)

        # Discrete params case
        vs2 = VolcMySQLVectorStore(
            host="localhost", port=3307, user="u", password="p", database="db", table_name="t2"
        )
        call2 = connect_mock.call_args_list[1]
        kwargs2 = call2.kwargs
        self.assertEqual(kwargs2.get("host"), "localhost")
        self.assertEqual(kwargs2.get("port"), 3307)
        self.assertEqual(kwargs2.get("user"), "u")
        self.assertEqual(kwargs2.get("password"), "p")
        self.assertEqual(kwargs2.get("database"), "db")

    @mock.patch("rds_mysql_vectorstore.vectorstore.pymysql.connect", create=True)
    def test_create_schema_executes_vector_index_ddl(self, connect_mock):
        conn = FakeConnection()
        connect_mock.return_value = conn
        vs = VolcMySQLVectorStore(
            host="h", user="u", password="p", database="d", table_name="docs"
        )
        vs.create_schema("docs", embedding_dim=4, algorithm_params={"distance": "l2", "using": "hnsw"})
        self.assertIsNotNone(conn.last_cursor)
        ddl = conn.last_cursor.last_sql or ""
        self.assertIn("VECTOR INDEX", ddl)

    @mock.patch("rds_mysql_vectorstore.vectorstore.pymysql.connect", create=True)
    def test_add_embeddings_executes_insert_with_to_vector(self, connect_mock):
        conn = FakeConnection()
        connect_mock.return_value = conn
        vs = VolcMySQLVectorStore(
            host="h", user="u", password="p", database="d", table_name="docs"
        )
        vectors = [[0.1, 0.2, 0.3, 0.4], [0.9, 0.8, 0.7, 0.6]]
        vs.add_embeddings(vectors=vectors, texts=["a", "b"])
        # Check that at least one INSERT used TO_VECTOR
        executed_sqls = [sql for (sql, _params) in conn.last_cursor.executed]
        self.assertTrue(any("TO_VECTOR" in sql for sql in executed_sqls))

    @mock.patch("rds_mysql_vectorstore.vectorstore.pymysql.connect", create=True)
    def test_similarity_search_by_vector_builds_order_by_limit(self, connect_mock):
        conn = FakeConnection()
        connect_mock.return_value = conn
        vs = VolcMySQLVectorStore(
            host="h", user="u", password="p", database="d", table_name="docs"
        )
        qvec = [0.1, 0.2, 0.3, 0.4]
        vs.similarity_search_by_vector(qvec, k=5)
        select_sql = conn.last_cursor.last_sql or ""
        self.assertIn("ORDER BY dist LIMIT", select_sql)
        # Optional stronger check: ensure TO_VECTOR in distance expression
        self.assertIn("TO_VECTOR(%s)", select_sql)

    @mock.patch("rds_mysql_vectorstore.vectorstore.pymysql.connect", create=True)
    def test_configure_session_validation_errors(self, connect_mock):
        connect_mock.return_value = FakeConnection()
        vs = VolcMySQLVectorStore(
            host="h", user="u", password="p", database="d", table_name="docs"
        )
        # Invalid distance value
        with self.assertRaises(ValueError):
            vs.configure_session(loose_default_vector_distance="manhattan")
        # Out of range ef_search
        with self.assertRaises(ValueError):
            vs.configure_session(loose_hnsw_ef_search=0)
        with self.assertRaises(ValueError):
            vs.configure_session(loose_hnsw_ef_search=10001)


if __name__ == "__main__":
    unittest.main()
