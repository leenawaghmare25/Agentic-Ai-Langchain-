from flask import Flask, redirect, url_for, session
from database import db
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'super-secret-key-12345'

    db.init_app(app)
    bcrypt.init_app(app)

    # Import routes inside factory to resolve circular dependency
    from routes import auth_bp, task_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('task.dashboard'))
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
