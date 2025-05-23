from sqlite3 import IntegrityError
import enum
from __init__ import app, db
from model.user import User
from datetime import datetime

class UploadStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

class ImageUpload(db.Model):
    __tablename__ = 'image_upload'
    id = db.Column(db.Text, primary_key=True)
    _filename = db.Column(db.Text, nullable=False)
    _upload_status = db.Column(db.Enum(UploadStatus), nullable=False)
    _created_at = db.Column(db.DateTime, nullable=False)
    _uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _s3_key = db.Column(db.Text, nullable=True)

    def __init__(self, id, filename, uid, upload_status):
        self.id = id
        self._filename = filename
        self._uid = uid
        self._upload_status = upload_status
        self._created_at = datetime.now()
        self.s3_key = None

    def __repr__(self):
        return f"ImageUpload(id={self.id}, uid={self._uid}, filename={self._filename}, upload_status={self._upload_status}, created_at={self._created_at}, s3_key={self._s3_key})"
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
      # read func  
    def read(self):
        user = User.query.get(self._uid)

        data = {
            "id": self.id,
            "filename": self._filename,
            "upload_status": self._upload_status,
            "user": {
                "name": user.read()["name"],
                "id": user.read()["id"],
                "uid": user.read()["uid"],
                "email": user.read()["email"],
                "pfp": user.read()["pfp"]
            },
            "created_at": self._created_at,
            "s3_key": self._s3_key
        }
        return data
    # update func
    def update(self):
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error
        # delete func
    def delete(self):  
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise error 
        
        