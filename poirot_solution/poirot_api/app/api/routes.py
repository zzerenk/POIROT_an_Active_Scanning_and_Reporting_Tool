from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Frontend klasöründeki sayfayı çağırıyoruz
    return render_template('pages/home.html')