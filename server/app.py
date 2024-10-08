#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):
    def delete(self):
        session.clear()  # Clear all session data
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:
            article = Article.query.filter(Article.id == id).first()
            return make_response(jsonify(article.to_dict()), 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data.get('username')

        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return {
                'message': 'User logged in successfully',
                'id': user.id,  # User ID
                'username': user.username  # Username added to the response
            }, 200
        else:
            return {'message': 'User not found'}, 404


class Logout(Resource):
    def delete(self):
        session.clear()  # Clear session data
        return {}, 204

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)  # Fetch the user from the database
            return {
                'id': user.id,                # User ID
                'username': user.username      # Username added to the response
            }, 200
        return {'message': 'No user logged in'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
