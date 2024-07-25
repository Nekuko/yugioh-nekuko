from flask import Flask, request, json, jsonify
from Simulator import Simulator
from ModifiableAttribute import Owner
from Summon import Summons

app = Flask(__name__)
simulator = Simulator()
simulator.start()


@app.route("/api", methods=["GET"])
def index():
    data = simulator.get_json()
    return jsonify(data)


@app.route("/api/request", methods=["POST"])
def api_request():
    data = json.loads(request.data)
    message = simulator.manage_request(data)
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)

