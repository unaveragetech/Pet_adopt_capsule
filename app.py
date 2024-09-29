from flask import Flask
from models import db
from config import Config
from routes import bp as main_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
