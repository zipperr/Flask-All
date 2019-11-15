from flask import Flask, send_file, render_template, request, redirect, url_for, make_response, jsonify, send_from_directory
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

#################### BBS ####################
# DB作成
# >>> from app import db
# >>> db.create_all()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"  # or "postgresql://localhost/flasknote"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 文章テーブル
class Article(db.Model):
    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)       # ID
    pub_dat   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)   # 日付
    name      = db.Column(db.String(80))                                          # 名前
    article   = db.Column(db.Text())                                              # 文章
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False) # スレッドID

    def __init__(self, pub_date, name, article, thread_id):
        self.pub_date = pub_date
        self.name = name
        self.article = article
        self.thread_id = thread_id


# スレッドテーブル
class Thread(db.Model):
    id         = db.Column(db.Integer,    primary_key=True)              # ID
    threadname = db.Column(db.String(80), unique=True)                   # スレッド名
    articles   = db.relationship('Article', backref='thread', lazy=True) # 文章テーブルと結合

    def __init__(self, threadname, articles=[]):
        self.threadname = threadname
        self.articles = articles


@app.route("/bbs")
def main():
    # スレッド取得
    threads = Thread.query.all()
    return render_template("bbs_index.html", threads=threads)


@app.route("/thread", methods=["POST"])
def thread():
    # スレッド取得
    thread_get = request.form["thread"]
    threads = Thread.query.all()
    thread_list = []
    threads = Thread.query.all()

    # スレッド名と一致したレコードをthread_listにappend
    for th in threads:
        thread_list.append(th.threadname)

    if thread_get in thread_list:
        # thread_listに紐づく文章取得
        thread = Thread.query.filter_by(threadname=thread_get).first()
        articles = Article.query.filter_by(thread_id=thread.id).all()
        return render_template("bbs_thread.html", articles=articles, thread=thread_get)
    else:
        # なければスレッド新規作成
        thread_new = Thread(thread_get)
        db.session.add(thread_new)
        db.session.commit()
        articles = Article.query.filter_by(thread_id=thread_new.id).all()
        return render_template("bbs_thread.html", articles=articles, thread=thread_get)


@app.route("/result", methods=["POST"])
def result():
    # 投稿内容インサート
    date = datetime.now()
    article = request.form["article"]
    name = request.form["name"]
    thread = request.form["thread"]
    thread = Thread.query.filter_by(threadname=thread).first()
    admin = Article(pub_date=date, name=name, article=article, thread_id=thread.id)
    db.session.add(admin)
    db.session.commit()
    return render_template("bbs_result.html", article=article, name=name, now=date)

#################### FileUploader ####################
@app.route("/")
def index():
    # ディレクトリ無ければ作る
    if not os.path.exists('uploadfile/'):
        os.makedirs('uploadfile/')

    files = os.listdir("./uploadfile/")
    return render_template("fileuploader_index.html", files=files)


# ファイルをアップロードする
@app.route('/Upload', methods=['POST'])
def upload_multipart():
    # ディレクトリ無ければ作る
    if not os.path.exists('uploadfile/'):
        os.makedirs('uploadfile/')

    # リクエストにファイルがない場合
    if 'uploadFile' not in request.files:
        make_response(jsonify({'result': 'uploadFile is required.'}))

    file = request.files['uploadFile']
    filename = file.filename

    # ファイル名null
    if '' == filename:
        make_response(jsonify({'result': 'filename must not empty.'}))

    # 同名ファイルが存在する場合
    if os.path.exists(filename):
        make_response(jsonify({'result': 'filename already exists.'}))

    file.save('uploadfile/' + filename)
    return redirect(url_for('index'))
    # return make_response(jsonify({'result':'upload OK.'}))

# ファイルを削除する
@app.route('/Delete/<string:filename>', methods=['GET'])
def Delete(filename):
    # ファイル名null
    if '' == filename:
        make_response(jsonify({'result': 'filename must not empty.'}))

    # ファイルがない場合
    if not os.path.isfile('uploadfile/' + filename):
        make_response(jsonify({'result': 'file not found.'}))

    os.remove('uploadfile/' + filename)
    return redirect(url_for('index'))
    # return make_response(jsonify({'result':'upload OK.'}))


# ファイルをダウンロードする
@app.route('/Download/<string:filename>', methods=['GET'])
def Download(filename):
    # ファイルがない場合
    if not os.path.isfile('uploadfile/' + filename):
        # make_response(jsonify({'result': 'file not found.'}))
        return redirect(url_for('index'))

    return send_file('uploadfile/' + filename)


# 画像ファイル表示
@app.route('/images/<path:filename>')
def send_image(filename):
    return send_from_directory('images/', filename)


####################   RestAPI    ####################
@app.route('/get_request', methods=['GET'])
def get_request():
    output = {
        "version": "1.0",
        "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "ハロー"
                }
            }
    }
    return jsonify(output)


@app.route('/post_request', methods=['POST'])
def post_request():
    output = {
        "version": "1.0",
        "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "ハロー"
                }
            }
    }
    return jsonify(output)


@app.route('/post_json', methods=['POST'])
def post_json():
    # jsonを受け取る
    json = request.get_json()
    # 受け取ったjsonを返す
    return jsonify(json)


@app.route('/get_json_from_dictionary', methods=['GET'])
def get_json_from_dictionary():
    dic = {
        'foo': 'bar',
        'ほげ': 'ふが'
    }
    # dictionaryをjsonへ変換して返す
    return jsonify(dic)


@app.route('/count/<int:i>', methods=['POST'])
def post_arg(i):
    return 'you posted {}\n'.format(i)
######################################################


if __name__ == "__main__":
    app.run(debug=True, threaded=True, host="0.0.0.0", port=8080)
    # app.run(debug=True, threaded=True, host="localhost", port=8080)