from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User
from model.imageUpload import ImageUpload
from datetime import datetime

class ImagePost(db.Model):
    __tablename__ = 'image_post'
    id = db.Column(db.Integer, primary_key=True)
    _description = db.Column(db.String(255), nullable=True)
    _title = db.Column(db.String(255), nullable=True)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _date_posted = db.Column(db.DateTime, nullable=False)

    def __init__(self, uid, title, description):
        self._uid = uid
        self._title = title
        self._description = description
        self._date_posted = datetime.now()

    def __repr__(self):
        return f"ImagePost(id={self.id}, uid={self._uid}, title={self._title}, description={self._description}, date_posted={self._date_posted})"
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        
    def read(self):
        user = User.query.get(self._uid)
        images = ImageUpload.query.filter(ImageUpload._post_id == self.id).all()

        data = {
            "id": self.id,
            "title": self._title,
            "description": self._description,
            "user": {
                "name": user.read()["name"],
                "id": user.read()["id"],
                "uid": user.read()["uid"],
                "email": user.read()["email"],
                "pfp": user.read()["pfp"]
            },
            "date_posted": self._date_posted,
            "images": [image.read() for image in images]
        }
        return data
    
    def update(self, inputs=None):
        if inputs:
            self._title = inputs.get("title", self._title)
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