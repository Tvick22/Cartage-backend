from flask import Blueprint, request, jsonify
from model.community import Community
from __init__ import db

community_api = Blueprint('community_api', __name__, url_prefix='/api/groups')

@community_api.route('', methods=['GET'])
def get_communities():
    communities = Community.query.all()
    return jsonify([c.read() for c in communities])

@community_api.route('', methods=['POST'])
def create_community():
    data = request.get_json()
    name = data.get("name")
    period = data.get("period")
    person_uids = data.get("personUids", [])

    if not name or not period:
        return jsonify({"error": "Missing name or period"}), 400

    community = Community(name, period)
    community.create()
    community.add_members_by_uids(person_uids)
    
    return jsonify(community.read()), 201

@community_api.route('/<int:community_id>', methods=['PUT'])
def update_community(community_id):
    community = Community.query.get(community_id)
    if not community:
        return jsonify({"error": "Community not found"}), 404
    
    data = request.get_json()
    community.update(data)
    return jsonify(community.read()), 200

@community_api.route('/<int:community_id>', methods=['DELETE'])
def delete_community(community_id):
    community = Community.query.get(community_id)
    if not community:
        return jsonify({"error": "Community not found"}), 404
    community.delete()
    return jsonify({"message": "Community deleted"}), 200
