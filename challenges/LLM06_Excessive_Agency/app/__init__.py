from flask import Flask

app = Flask(__name__)
app.secret_key = "S3cr3t_K3y_LLM06_Ex3ss1ve_4gency"
app.config['SESSION_PERMANENT'] = False

from app import routes
