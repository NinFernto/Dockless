from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Привет, это Flask!"

@app.route("/api/hello")
def hello():
    name = request.args.get("name", "мир")
    return jsonify(message=f"Привет, {name}!")

if __name__ == "__main__":
    app.run(debug=True)
