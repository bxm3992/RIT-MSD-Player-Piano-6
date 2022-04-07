from flask import Flask, render_template, request, json
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        return "Get method"
    elif request.method == 'POST':
        return "Post method"
    else:
        return "Ok"


if __name__ == "__main__":
    app.run(debug=True)