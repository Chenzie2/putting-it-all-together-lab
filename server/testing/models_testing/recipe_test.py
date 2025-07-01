import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, User, Recipe

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        with app.app_context():
            db.create_all()
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="TestUser1")
            user.password_hash = "securepassword"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert "Ham him compass" in new_recipe.instructions
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            db.create_all()
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="TestUser2")
            user.password_hash = "securepassword"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                instructions="Long enough instructions for testing validation to pass.",
                minutes_to_complete=45,
                user_id=user.id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''must raise error for instructions less than 50 characters.'''
        with app.app_context():
            db.create_all()
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(username="TestUser3")
            user.password_hash = "securepassword"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Short Instructions",
                minutes_to_complete=20,
                user_id=user.id
            )

            with pytest.raises(ValueError):
                recipe.instructions = "Too short."
                db.session.add(recipe)
                db.session.commit()