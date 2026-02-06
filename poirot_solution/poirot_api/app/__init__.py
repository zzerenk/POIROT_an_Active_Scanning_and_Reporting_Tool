import os
from flask import Flask
from config import Config

def create_app(config_class=Config):
    # 1. Klasör yollarını hesapla (Matematik kısmı)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # .../poirot_api
    root_dir = os.path.dirname(base_dir) # .../poirot_solution
    
    # Web klasörünün tam yolu
    web_folder = os.path.join(root_dir, 'poirot_web')
    template_folder = os.path.join(web_folder, 'templates')
    static_folder = os.path.join(web_folder, 'static')

    # 2. Flask'ı başlat ve yolları göster
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    
    app.config.from_object(config_class)

    # 3. Rotaları (Blueprint) içeri al
    from app.api.routes import main
    app.register_blueprint(main)

    return app