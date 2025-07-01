from flask import Flask, request, jsonify, session
from flask_migrate import Migrate
from flask_cors import CORS
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecret'
app.json.compact = False

CORS(app, supports_credentials=True)

db.init_app(app)
migrate = Migrate(app, db)


def format_errors(errors):
    return {'errors': errors}


class Signup(MethodView):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        errors = []

        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        if errors:
            return format_errors(errors), 422

        try:
            user = User(username=username, bio=bio, image_url=image_url)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return jsonify(user.to_dict()), 201

        except IntegrityError:
            db.session.rollback()
            return format_errors(["Username must be unique."]), 422


class CheckSession(MethodView):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_dict()), 200
        return {'error': 'User not found'}, 401


class Login(MethodView):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return jsonify(user.to_dict()), 200

        return {'error': 'Invalid username or password'}, 401


class Logout(MethodView):
    def delete(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized'}, 401

        session['user_id'] = None
        return {}, 204


class RecipeIndex(MethodView):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()
        return jsonify([recipe.to_dict() for recipe in recipes]), 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        errors = []

        title = data.get('title')
        instructions = data.get('instructions')
        minutes = data.get('minutes_to_complete')

        if not title:
            errors.append("Title is required.")
        if not instructions or len(instructions) < 50:
            errors.append("Instructions must be at least 50 characters long.")

        if errors:
            return format_errors(errors), 422

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes,
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()
            return jsonify(recipe.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return format_errors(["Failed to create recipe."]), 422


# Register routes
app.add_url_rule('/signup', view_func=Signup.as_view('signup'))
app.add_url_rule('/check_session', view_func=CheckSession.as_view('check_session'))
app.add_url_rule('/login', view_func=Login.as_view('login'))
app.add_url_rule('/logout', view_func=Logout.as_view('logout'))
app.add_url_rule('/recipes', view_func=RecipeIndex.as_view('recipes'))

if __name__ == '__main__':
    app.run(port=5555, debug=True)
