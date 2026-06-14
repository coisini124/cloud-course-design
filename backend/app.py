from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/ping')
def ping():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # 必须监听 0.0.0.0，否则容器外无法访问
    app.run(host='0.0.0.0', port=5000)