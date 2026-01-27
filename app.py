from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return "Привет, это Flask!"

@app.route("/api/hello")
def hello():
    name = request.args.get("name", "мир")
    return jsonify(message=f"Привет, {name}!")

# subprocess.Popen(
#     ["python", "worker.py", "--mode", "auto"],
# )

if __name__ == "__main__":
    app.run(debug=True)
