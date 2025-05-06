from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User
from datetime import datetime

class Road(db.Model):
    __tablename__ = 'Roads'
    id = db.Column(db.Integer, primary_key=True)
    _road_name = db.Column(db.String(255), nullable=True)

    def __init__(self, road_name):
        self._road_name = road_name

    def __repr__(self):
        return f"Review(id={self.id}, road_name={self._road_name})"
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    def read(self):
        data = {
            "id": self.id,
            "road_name": self._road_name,
        }
        return data
    
    def update(self, inputs=None):
        if inputs:
            self._road_name = inputs.get("road_name", self._road_name)
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