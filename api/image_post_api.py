import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.imagePost import ImagePost
from api.upload_image import UploadAPI
import base64
import json

image_post_api = Blueprint('image_post_api', __name__, url_prefix='/api')

api = Api(image_post_api)

class ReviewAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):

            current_user = g.current_user

            data = request.get_json()
            
            if not data:
                return 400
            
            if not data["title"] or not data["description"]:
                return 400

            post = ImagePost(current_user.id, data["title"], data["description"])

            post.create() ## Create the post DB entry with an ID

            post_id = post.id

            return jsonify(post.read())
        
        def get(self):
            posts = ImagePost.query.all()

            if posts is None:
                return Response("{'message': 'Posts not found'}", 404)
                                                                                                                                                               
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify([post.read() for post in posts])

        @token_required()
        def put(self):

            current_user = g.current_user

            data = request.get_json()

            post = ImagePost.query.get(data['id'])

            if not post:
                return Response(jsonify({"message": "post not found"}), 404)
            
            if post._uid != current_user.id and current_user._role != "Admin":
                return Response(jsonify({"message": "can not update post"}), 401)
            
            if data['description']:
                post._description = data['description']

            if data['title']:
                post._rating = data['title']
            
            post.update()

            return jsonify(post.read())

        @token_required()
        def delete(self):

            current_user = g.current_user

            data = request.get_json()

            post = ImagePost.query.get(data['id'])

            if current_user._role == "Admin":
                post.delete()
                return Response(jsonify({"message": "Post removed", "deleted": True}), 200)

            if current_user.id != post._uid:
                return Response(jsonify({"message": "Post not deleted wrong user", "deleted": False}), 401)

            post.delete()

            return Response(jsonify({"message": "Post removed", "deleted": True}), 200)

    api.add_resource(_CRUD, '/post')