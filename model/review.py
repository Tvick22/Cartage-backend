from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User
from datetime import datetime
from model.roads import Road

# DO THE RELATIONAL COLUMN FOR ROAD ID

class Review(db.Model):
    __tablename__ = 'Reviews'
    id = db.Column(db.Integer, primary_key=True)
    _road_id = db.Column(db.Integer, db.ForeignKey('Roads.id'), nullable=False)
    _description = db.Column(db.String(255), nullable=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _rating = db.Column(db.Integer, nullable=False)
    _date_posted = db.Column(db.DateTime, nullable=False)

    def __init__(self, uid, road_id, description, rating):
        self._uid = uid
        self._road_id = road_id
        self._description = description
        self._rating = rating
        self._date_posted = datetime.now()

    def __repr__(self):
        return f"Review(id={self.id}, uid={self._uid}, road_id={self._road_id}, description={self._description}, rating={self._rating} date_posted={self._date_posted})"
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    def read(self):
        user = User.query.get(self._uid)
        road = Road.query.get(self._road_id)

        data = {
            "id": self.id,
            "road": road.read(),
            "description": self._description,
            "rating": self._rating,
            "user": {
                "name": user.read()["name"],
                "id": user.read()["id"],
                "uid": user.read()["uid"],
                "email": user.read()["email"],
                "pfp": user.read()["pfp"]
            },
            "date_posted": self._date_posted
        }
        return data
    
    def update(self, inputs=None):
        if inputs:
            self._rating = inputs.get("rating", self._rating)
            self._road_id = inputs.get("road_id", self._road_id)
            self._description = inputs.get("description", self._description)
            self._uid = inputs.get("uid", self._uid)
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    def delete(self):  
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    # def restore(data):
    #     users = {}
    #     for carPost_data in data:
    #         id = carPost_data.get("id")
    #         post = CarPost.query.filter_by(id=id).first()
    #         if post:
    #             post.update(carPost_data)
    #         else:
    #             print(carPost_data)
    #             post = CarPost(carPost_data.get("title"), carPost_data.get("description"), carPost_data.get("user").get("id"), carPost_data.get("car_type"), carPost_data.get("image_url_table"), carPost_data.get("date_posted"))
    #             post.create()
    #     return users