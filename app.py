import os
import json
from flask import Flask, request, jsonify, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import csv
from chromadb_handler import ChromaDBHandler

# 設定
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

# ChromaDBハンドラーの初期化
db_handler = ChromaDBHandler(
    collection_name="test-collection",
    persist_directory="./chromadb"
)

# アップロード可能なファイルかどうかを確認する関数
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# データ挿入のエンドポイント
@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.get_json()
    ids = data.get('ids')
    documents = data.get('documents')
    try:
        response = db_handler.insert(ids, documents)
        print(response)

        return app.response_class(response=json.dumps({'status': 'success'}, ensure_ascii=False), mimetype='application/json'), 200
    except ValueError as ve:
        return app.response_class(response=json.dumps({'error': str(ve)}, ensure_ascii=False), mimetype='application/json'), 400
    except Exception as e:
        return app.response_class(response=json.dumps({'error': '内部エラー'}, ensure_ascii=False), mimetype='application/json'), 500

# すべてのドキュメントを表示するエンドポイント
@app.route('/list_all_documents', methods=['GET'])
def list_all_documents():
    try:
        all_documents = db_handler.list_all_documents()
        return app.response_class(response=json.dumps(all_documents, ensure_ascii=False), mimetype='application/json'), 200
    except Exception as e:
        return app.response_class(response=json.dumps({'error': '内部エラー'}, ensure_ascii=False), mimetype='application/json'), 500

# データ削除のエンドポイント
@app.route('/delete', methods=['POST'])
def delete_data():
    data = request.get_json()
    ids = data.get('ids')
    try:
        db_handler.delete(ids)
        return app.response_class(response=json.dumps({'status': 'success'}, ensure_ascii=False), mimetype='application/json'), 200
    except ValueError as ve:
        return app.response_class(response=json.dumps({'error': str(ve)}, ensure_ascii=False), mimetype='application/json'), 400
    except Exception as e:
        return app.response_class(response=json.dumps({'error': str(e)}, ensure_ascii=False), mimetype='application/json'), 500

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
        return app.response_class(response=json.dumps(query_results, ensure_ascii=False), mimetype='application/json'), 200
    except ValueError as ve:
        return app.response_class(response=json.dumps({'error': str(ve)}, ensure_ascii=False), mimetype='application/json'), 400
    except Exception as e:
        return app.response_class(response=json.dumps({'error': '内部エラー'}, ensure_ascii=False), mimetype='application/json'), 500

# CSVファイルアップロードのエンドポイント
@app.route('/csv-upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # ファイルがPOSTリクエストに含まれているか確認
        if 'file' not in request.files:
            flash('ファイルが見つかりません。')
            return redirect(request.url)

        file = request.files['file']

        # ファイル名が空でないか確認
        if file.filename == '':
            flash('選択されたファイルがありません。')
            return redirect(request.url)

        # ファイルが許可された拡張子か確認
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # アップロードフォルダが存在しない場合は作成
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash('ファイルが正常にアップロードされました。')

            # CSVファイルの内容を読み取り、ChromaDBに挿入
            ids = []
            documents = []
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    header = next(reader, None)  # ヘッダーがある場合はスキップ
                    for row_number, row in enumerate(reader, start=2):  # 2行目から開始
                        if len(row) < 2:
                            flash(f'行 {row_number} に十分なデータがありません。スキップされました。')
                            continue
                        id_value = row[0].strip()
                        document_value = row[1].strip()
                        if not id_value or not document_value:
                            flash(f'行 {row_number} に空のIDまたはドキュメントがあります。スキップされました。')
                            continue
                        ids.append(id_value)
                        documents.append(document_value)

            except Exception as e:
                flash(f'CSVファイルの読み取り中にエラーが発生しました: {str(e)}')
                return redirect(request.url)

            if not ids or not documents:
                flash('有効なデータがCSVファイルに含まれていません。')
                return redirect(request.url)

            # ChromaDBにデータを挿入
            try:
                db_handler.insert(ids, documents)
                flash(f'合計 {len(ids)} 件のデータがChromaDBに挿入されました。')
            except ValueError as ve:
                flash(f'DBへの挿入中にエラーが発生しました: {str(ve)}')
            except Exception as e:
                flash(f'DBへの挿入中に予期せぬエラーが発生しました: {str(e)}')

            return redirect(url_for('upload_file'))
        else:
            flash('CSVファイルのみアップロード可能です。')
            return redirect(request.url)

    return render_template('upload.html')

@app.route('/query-ui', methods=['GET'])
def query_ui():
    return render_template('query.html')

@app.route('/list-documents', methods=['GET'])
def list_documents():
    return render_template('list_documents.html')


if __name__ == '__main__':
    app.run(debug=True)

# GitBashからのリクエストコマンド
# /list_all_documents エンドポイントに GET リクエストを送信するための GitBash コマンド
# GitBash コマンド:
# curl http://127.0.0.1:5000/list_all_documents