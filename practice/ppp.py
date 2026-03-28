from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)


@app.route('/sum')
def sum_ab():
    """
    ---
    responses:
      200:
        description: Результат сложения
    """
    a = 5276984796
    b = 394706740
    return str(a + b)

@app.route('/')
def home():
    """
    ---
    responses:
      200:
        description: Главная страница
    """
    return "Сервер работает"

if __name__ == '__main__':
    app.run(port=5000)


#pip install flask
# pip install flasgger
# pip install  flask-restx