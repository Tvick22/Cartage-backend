import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app
from api.jwt_authorize import token_required
from model.roads import Road
import base64
import json

roads_api = Blueprint('roads_api', __name__, url_prefix='/api')

api = Api(roads_api)

class RoadAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):

            current_user = g.current_user

            if current_user._role != "Admin":
                return Response(jsonify({"message": "can not create road"}), 401)

            data = request.get_json()

            if not data or not "road_name" in data:
                return Response("{'message': 'bad data'}", 400)

            road = Road(data['road_name'])

            road.create()

            return jsonify(road.read())
        
        def get(self):
            roads = Road.query.all()

            if roads is None:
                return Response("{'message': 'Roads not found'}", 404)
                                                                                                                                                               
            # Return response to the client in JSON format, converting Python dictionaries to JSON format
            return jsonify([road.read() for road in roads])

        @token_required()
        def put(self):

            current_user = g.current_user

            data = request.get_json()

            road = Road.query.get(data['id'])

            if not road:
                return Response(jsonify({"message": "road not found"}), 404)
            
            if road._uid != current_user.id and current_user._role != "Admin":
                return Response(jsonify({"message": "can not update road"}), 401)
            
            if data['road_name']:
                road._road_name = data['road_name']
            
            road.update()

            return jsonify(road.read())

        @token_required()
        def delete(self):

            current_user = g.current_user

            data = request.get_json()

            road = Road.query.get(data['id'])

            if current_user._role == "Admin":
                road.delete()
                return Response(jsonify({"message": "Post removed", "deleted": True}), 200)

            if current_user.id != road._uid:
                return Response(jsonify({"message": "Post not deleted wrong user", "deleted": False}), 401)

            road.delete()

            return Response(jsonify({"message": "Road removed", "deleted": True}), 200)

    api.add_resource(_CRUD, '/roads')