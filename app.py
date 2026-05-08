import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template
from config import Config
from utils.db import mysql

# Blueprints
from routes.attendance_routes import attendance
from routes.auth_routes import auth
from routes.teacher_routes import teacher
from routes.student_routes import student

app = Flask(__name__)

app.config.from_object(Config)

mysql.init_app(app)

# Register Blueprints
app.register_blueprint(attendance)
app.register_blueprint(auth)
app.register_blueprint(teacher)
app.register_blueprint(student)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(
    debug=True,
    host='0.0.0.0',
    port=8000
)