from flask import Flask

app = Flask(__name__)
app.secret_key = "S3cr3t_K3y_LLM09_M1s1nf0rm@t10n"
app.config['SESSION_PERMANENT'] = False

from app import routes
