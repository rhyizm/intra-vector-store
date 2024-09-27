# app.py

from flask import Flask, request, jsonify
from chromadb_handler import ChromaDBHandler

app = Flask(__name__)

app.config['DEBUG'] = True

# ChromaDBハンドラーの初期化
db_handler = ChromaDBHandler()

# データ挿入のエンドポイント
@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.get_json()
    ids = data.get('ids')
    documents = data.get('documents')
    try:
        response = db_handler.insert(ids, documents)
        print(response)

        return jsonify({'status': 'success'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': '内部エラー'}), 500

# データ削除のエンドポイント
@app.route('/delete', methods=['POST'])
def delete_data():
    data = request.get_json()
    ids = data.get('ids')
    try:
        db_handler.delete(ids)
        return jsonify({'status': 'success'}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# データ検索のエンドポイント
@app.route('/query', methods=['POST'])
def query_data():
    data = request.get_json()
    query_texts = data.get('query_texts')
    n_results = data.get('n_results', 5)
    try:
        query_results = db_handler.query(
            query_texts=query_texts,
            n_results=n_results
        )
        return jsonify(query_results), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': '内部エラー'}), 500

if __name__ == '__main__':
    app.run()
