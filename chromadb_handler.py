# chromadb_handler.py

from chromadb import PersistentClient
from embeddings import create_embeddings

class ChromaDBHandler:
    """
    ChromaDBHandler クラスは、ChromaDB を操作するためのハンドラです。
    
    このクラスを使用すると、ドキュメントの挿入、削除、およびクエリを簡単に実行できます。
    
    ## 使用例
    
    ```python
    from chromadb_handler import ChromaDBHandler
    
    # ハンドラの初期化
    db_handler = ChromaDBHandler(
        collection_name="test-collection",
        persist_directory="./chromadb"
    )
    
    # データの挿入
    ids = ["test-id-1", "test-id-2", "test-id-3"]
    documents = ["リンゴ", "ゴリラ", "ラッパ"]
    db_handler.insert(ids, documents)
    
    # データのクエリ
    results = db_handler.query(query_texts=["ギター"], n_results=1)
    print(results)
    
    # データの削除
    db_handler.delete(ids)
    ```
    
    ## パラメータ
    - `collection_name` (str): 使用するコレクションの名前。デフォルトは `"test-collection"`。
    - `persist_directory` (str): ChromaDB のデータを永続化するディレクトリのパス。デフォルトは `"./chromadb"`。
    
    ## メソッド
    
    ### `__init__(self, collection_name="test-collection", persist_directory="./chromadb")`
    クラスのコンストラクタ。ChromaDB クライアントを初期化し、指定されたコレクションを取得または作成します。
    
    **パラメータ:**
    - `collection_name` (str): 使用するコレクションの名前。
    - `persist_directory` (str): データを永続化するディレクトリのパス。
    
    ### `_get_or_create_collection(self)`
    指定されたコレクションが存在するかを確認し、存在しない場合は新規に作成します。
    
    **戻り値:**
    - `chromadb.Collection`: 取得または作成されたコレクションオブジェクト。
    
    ### `insert(self, ids, documents)`
    ドキュメントをコレクションに挿入します。各ドキュメントには一意の ID が必要です。
    
    **パラメータ:**
    - `ids` (List[str]): 挿入する各ドキュメントの一意な ID のリスト。
    - `documents` (List[str]): 挿入するドキュメントのリスト。
    
    **例外:**
    - `ValueError`: `ids` または `documents` が空の場合に発生します。
    
    ### `delete(self, ids)`
    指定された ID のドキュメントをコレクションから削除します。
    
    **パラメータ:**
    - `ids` (List[str]): 削除するドキュメントの ID のリスト。
    
    **例外:**
    - `ValueError`: `ids` が空の場合に発生します。
    
    ### `query(self, query_texts, n_results=5)`
    指定されたクエリテキストに基づいて、類似したドキュメントを検索します。
    
    **パラメータ:**
    - `query_texts` (List[str]): 検索クエリとして使用するテキストのリスト。
    - `n_results` (int): 返される最大の結果数。デフォルトは `5`。
    
    **戻り値:**
    - `dict`: クエリ結果を含む辞書。キーには `'ids'`、`'documents'` などが含まれます。
    """

    def __init__(self, collection_name="test-collection", persist_directory="./chromadb"):
        """
        クラスのコンストラクタ。ChromaDB クライアントを初期化し、指定されたコレクションを取得または作成します。

        :param collection_name: 使用するコレクションの名前。デフォルトは "test-collection"。
        :param persist_directory: データを永続化するディレクトリのパス。デフォルトは "./chromadb"。
        """
        self.client = PersistentClient(path=persist_directory)
        self.collection = self._get_or_create_collection(collection_name=collection_name)
        self.collection_name = collection_name

    def _get_or_create_collection(self, collection_name):
        """
        指定されたコレクションが存在するかを確認し、存在しない場合は新規に作成します。

        :return: 取得または作成されたコレクションオブジェクト。
        """
        collections = self.client.list_collections()

        for collection in collections:
            if collection.name == collection_name:
                return self.client.get_collection(collection_name)
            else:
                return self.client.create_collection(collection_name)

    def insert(self, ids, documents):
        """
        ドキュメントをコレクションに挿入します。各ドキュメントには一意の ID が必要です。

        :param ids: 挿入する各ドキュメントの一意な ID のリスト。
        :param documents: 挿入するドキュメントのリスト。
        :raises ValueError: ids または documents が空の場合に発生。
        """
        if not ids or not documents:
            raise ValueError("ids、embeddings、documentsは全て必須です")
        
        embeddings = create_embeddings(documents)

        result = self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents
        )

        return result

    def delete(self, ids):
        """
        指定された ID のドキュメントをコレクションから削除します。

        :param ids: 削除するドキュメントの ID のリスト。
        :raises ValueError: ids が空の場合に発生。
        """
        if not ids:
            raise ValueError("idsは必須です")
        self.collection.delete(ids=ids)

    def query(self, query_texts, n_results=5):
        """
        指定されたクエリテキストに基づいて、類似したドキュメントを検索します。

        :param query_texts: 検索クエリとして使用するテキストのリスト。
        :param n_results: 返される最大の結果数。デフォルトは 5。
        :return: クエリ結果を含む辞書。キーには 'ids'、'documents' などが含まれます。
        """
        query_embeddings = create_embeddings(query_texts)

        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
