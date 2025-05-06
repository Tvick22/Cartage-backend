import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.carPost import CarPost
from model.carPostImage import carPostImage_base64_upload
import base64
import json

"""
This Blueprint object is used to define APIs for the Post model.
- Blueprint is used to modularize application files.
- This Blueprint is registered to the Flask app in main.py.
"""
carPost_api = Blueprint('carPost_api', __name__, url_prefix='/api')

"""
The Api object is connected to the Blueprint object to define the API endpoints.
- The API object is used to add resources to the API.
- The objects added are mapped to code that contains the actions for the API.
- For more information, refer to the API docs: https://flask-restful.readthedocs.io/en/latest/api.html
"""
api = Api(carPost_api)

class CarPostAPI:
    """
    Define the API CRUD endpoints for the Post model.
    There are four operations that correspond to common HTTP methods:
    - post: create a new post
    - get: read posts
    - put: update a post
    - delete: delete a post
    """
    class _CRUD(Resource):
        @token_required()
        def post(self):
            # Obtain the current user from the token required setting in the global context
            current_user = g.current_user
            # Obtain the request data sent by the RESTful client API
            data = request.get_json()

            if "title" not in data or "description" not in data or "car_type" not in data or "image_base64_table" not in data:
                return Response("{'message': 'Missing required fields'}", 400)

            # Create a new post object using the data from the request
            post = CarPost(data['title'], data['description'], current_user.id, data['car_type'], "[]")
            # Save the post object using the Object Relational Mapper (ORM) method defined in the model
            post.create()

            # Convert the image_base64_table to a list of strings
            image_url_table = []
            for i in range(len(data['image_base64_table'])):
                base64_image = data['image_base64_table'][i]["base64"]
                name = data['image_base64_table'][i]["name"]
                if image_url_table.count(name) > 0:
                    # If the name already exists, append a number to the end of the name
                    # This is to prevent duplicate image names
                    newName = name.replace(".", f"_{i}.", 1)
                    name = newName
                print(base64_image)
                carPostImage_base64_upload(base64_image, post.id, name)
                image_url_table.append(name)
            post.updateImageTable(image_url_table)

            # for base64_image in data['image_base64_table']:
            #     print(base64_image)
            #     carPostImage_base64_upload(base64_image, post.id, )

            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify(post.read())
        
        def get(self):
            posts = CarPost.query.all()

            if posts is None:
                return Response("{'message': 'Post not found'}", 404)
                                                                                                                                                               
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify([post.read() for post in posts])

        @token_required()
        def put(self):
            # Obtain the current user
            current_user = g.current_user
            # Obtain the request data
            data = request.get_json()
            # Find the current post from the database table(s)
            post = CarPost.query.get(data['id'])
            # Update the post
            post._title = data['title']
            post._description = data['description']
            post._car_type = data['car_type']
            #post._image_url_table = data['image_url_table']
            # Save the post
            post.update()
            # Return response
            return jsonify(post.read())

        @token_required()
        def delete(self):
            # Obtain the current user
            current_user = g.current_user
            # Obtain the request data
            data = request.get_json()
            # Find the current post from the database table(s)
            post = CarPost.query.get(data['id'])

            if current_user._role == "Admin":
                post.delete()
                return jsonify({"message": "Post deleted",
                            "deleted": True})

            if current_user.id != post.read()['user']['id']:
                return jsonify({"message": "Post not deleted wrong user",
                                "deleted": False})
            # Delete the post using the ORM method defined in the model
            post.delete()
            # Return response
            return jsonify({"message": "Post deleted",
                            "deleted": True})

    """
    Map the _CRUD class to the API endpoints for /post.
    - The API resource class inherits from flask_restful.Resource.
    - The _CRUD class defines the HTTP methods for the API.
    """
    api.add_resource(_CRUD, '/carPost')