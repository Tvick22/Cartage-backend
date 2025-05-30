from datetime import datetime
from __init__ import db
from model.user import User

# Association table for many-to-many relationship between users and communities
community_members = db.Table('community_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('community_id', db.Integer, db.ForeignKey('communities.id'))
)

class Community(db.Model):
    __tablename__ = 'communities'
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(100), nullable=False)
    _period = db.Column(db.String(50), nullable=True)
    _created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('User', secondary=community_members, backref='communities', lazy='dynamic')

    def __init__(self, name, period):
        self._name = name
        self._period = period

    def __repr__(self):
        return f"<Community {self.id} {self._name}>"

    def create(self):
        db.session.add(self)
        db.session.commit()

    def read(self):
        return {
            "id": self.id,
            "name": self._name,
            "period": self._period,
            "created_at": self._created_at,
            "members": [member.read() for member in self.members]
        }

    def update(self, data):
        self._name = data.get("name", self._name)
        self._period = data.get("period", self._period)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def add_members_by_uids(self, uids):
        for uid in uids:
            user = User.query.filter_by(id=uid).first()
            if user:
                self.members.append(user)
        db.session.commit()
