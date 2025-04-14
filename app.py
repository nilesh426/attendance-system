from flask import Flask
from extensions import db, migrate, login_manager
from models import Teacher

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return db.session.get(Teacher, int(user_id))

    from routes import register_routes
    register_routes(app)

    return app

# For CLI and flask run
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
