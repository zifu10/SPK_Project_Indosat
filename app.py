# ============================================================
# app.py — Entry Point Aplikasi Flask
# SPK Indosat Ooredoo Hutchison
# ============================================================

from flask import Flask
from config import Config
from routes.main import main_bp
from routes.data import data_bp
from routes.spk  import spk_bp
from routes.ml   import ml_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(spk_bp,  url_prefix='/spk')
app.register_blueprint(ml_bp,   url_prefix='/ml')


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
