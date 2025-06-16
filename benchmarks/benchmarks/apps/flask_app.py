import time

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def root():
    return jsonify({"message": "Hello World"})


@app.route("/json")
def json_endpoint():
    return jsonify(
        {
            "string": "Hello World",
            "number": 42,
            "boolean": True,
            "array": [1, 2, 3],
            "object": {"key": "value"},
        }
    )


@app.route("/echo", methods=["POST"])
def echo():
    return jsonify(request.get_json())


@app.route("/delay/<float:seconds>")
def delay(seconds):
    time.sleep(seconds)
    return jsonify({"message": f"Delayed for {seconds} seconds"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001)
