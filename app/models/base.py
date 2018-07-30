from app.utils import db, datetime
from sqlalchemy import exc


class BaseModel(db.Model):
	
	__abstract__ = True
	
	id = db.Column(db.Integer(), primary_key=True)
	created_at = db.Column(db.DateTime(), default=datetime.now())
	updated_at = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())
	
	def save(self):
		try:
			db.session.add(self)
			db.session.commit()
		except (exc.IntegrityError, exc.InvalidRequestError):
			db.session().rollback()
	
	def delete(self):
		db.session.delete(self)
		db.session.commit()

