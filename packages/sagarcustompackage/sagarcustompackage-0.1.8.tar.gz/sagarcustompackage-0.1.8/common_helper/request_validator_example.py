from flask import Flask, jsonify
from common_helper.request_validator import validate_request

app = Flask(__name__)

@app.route("/register", methods=["POST"])
@validate_request( schema={ "username": {"type": str, "required": True}, "age": {"type": int, "required": False} } )
def register(data):
    return jsonify({"status": "success", "data": data})


if __name__ == "__main__":
    app.run(debug=True)
