import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.review import Review
from model.roads import Road
import base64
import json

review_api = Blueprint('review_api', __name__, url_prefix='/api')

api = Api(review_api)

class ReviewAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):

            current_user = g.current_user

            data = request.get_json()

            if not data or not "road_name" in data or not "description" in data or not "rating" in data:
                return Response("{'message': 'bad data'}", 400)
            
            road = Road.query.filter_by(_road_name=data["road_name"]).first()

            if not road:
                road = Road(data["road_name"])
                road.create()

            review = Review(current_user.id, road.id, data["description"], data['rating'])

            review.create()

            return jsonify(review.read())
        
        def get(self):
            reviews = Review.query.all()

            if reviews is None:
                return Response("{'message': 'Reviews not found'}", 404)
                                                                                                                                                               
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify([review.read() for review in reviews])

        @token_required()
        def put(self):

            current_user = g.current_user

            data = request.get_json()

            review = Review.query.get(data['id'])

            if not review:
                return Response(jsonify({"message": "review not found"}), 404)
            
            if review._uid != current_user.id and current_user._role != "Admin":
                return Response(jsonify({"message": "can not update review"}), 401)
            
            if data['description']:
                review._description = data['description']

            if data['rating']:
                review._rating = data['rating']
            
            review.update()

            return jsonify(review.read())

        @token_required()
        def delete(self):

            current_user = g.current_user

            data = request.get_json()

            review = Review.query.get(data['id'])

            if current_user._role == "Admin":
                review.delete()
                return Response(jsonify({"message": "Road removed", "deleted": True}), 200)

            if current_user.id != review._uid:
                return Response(jsonify({"message": "Road not deleted wrong user", "deleted": False}), 401)

            review.delete()

            return Response(jsonify({"message": "Road removed", "deleted": True}), 200)

    api.add_resource(_CRUD, '/review')