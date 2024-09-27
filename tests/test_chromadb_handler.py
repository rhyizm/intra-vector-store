# tests/test_chromadb_handler.py

import pytest
import tempfile
from chromadb_handler import ChromaDBHandler
from embeddings import create_embeddings

@pytest.fixture(scope="module")
def db_handler():
    # テスト用の一時ディレクトリを作成
    test_persist_directory = tempfile.mkdtemp()
    handler = ChromaDBHandler(
        collection_name="test-collection",
        persist_directory=test_persist_directory
    )
    yield handler

def test_insert(db_handler):
    ids = ["test-id-1", "test-id-2", "test-id-3"]
    documents = ["リンゴ", "ゴリラ", "ラッパ"]

    db_handler.insert(ids, documents=documents)
    
    # 挿入されたデータをクエリで確認
    results = db_handler.query(query_texts=["ギター"], n_results=1)

    print(results)

    assert results['ids'][0][0] == "test-id-3"
    assert results['documents'][0][0] == "ラッパ"

def test_delete(db_handler):
    ids = ["test-id-1", "test-id-2", "test-id-3"]
    db_handler.delete(ids)
    
    # 削除されたデータが存在しないことを確認
    results = db_handler.query(query_texts=["テストドキュメント1"], n_results=1)
    assert "test-id-1" not in results['ids'][0]

def test_query_without_data(db_handler):
    # データが存在しない状態でクエリを実行
    results = db_handler.query(query_texts=["テストドキュメント1"], n_results=5)
    assert len(results['ids'][0]) == 0
