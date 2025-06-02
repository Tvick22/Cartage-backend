from flask import Blueprint, jsonify, request
from model.community import Community
from model.user import User
from __init__ import db

communities_api = Blueprint('communities_api', __name__, url_prefix='/api/groups')

@communities_api.route('', methods=['GET'])
def get_all_communities():
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', '', type=str)

    query = Community.query

    if search:
        query = query.filter(Community._name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(_category=category)

    communities = query.all()
    result = []
    for c in communities:
        result.append({
            "id": c.id,
            "name": c._name,
            "category": c._category,
            "cover_photo_url": c._cover_photo_url,
            "members": [
                {"uid": u.uid, "name": u.name, "email": u.email}
                for u in c.members
            ]
        })
    return jsonify(result)


@communities_api.route('', methods=['POST'])
def create_community():
    data = request.get_json()
    name = data.get("name")
    category = data.get("category")
    personUids = data.get("personUids", [])

    if not name or not category:
        return jsonify({"error": "Name and category are required"}), 400

    community = Community(name=name, category=category)

    for uid in personUids:
        user = User.query.filter_by(uid=uid).first()
        if user:
            community.members.append(user)

    db.session.add(community)
    db.session.commit()

    return jsonify({"message": "Community created", "id": community.id}), 201
