from flask import Blueprint, jsonify, request
from models.community import Community
from models.user import User
from database import db

bp = Blueprint('communities_api', __name__, url_prefix='/api/groups')

@bp.route('', methods=['GET'])
def get_all_communities():
    communities = Community.query.all()
    result = []
    for c in communities:
        result.append({
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "members": [
                {"uid": u.uid, "name": u.name, "email": u.email}
                for u in c.members
            ]
        })
    return jsonify(result)

@bp.route('', methods=['POST'])
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
