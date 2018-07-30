from .base import BaseModel, db, datetime


class Guest(BaseModel):
	
	__tablename__ = 'guests'
	
	guest_name = db.Column(db.String(100), nullable=False)
	host_name = db.Column(db.String(100), nullable=False)
	host_email = db.Column(db.String(100), nullable=False)
	host_slackid = db.Column(db.String(100), nullable=False)
	purpose = db.Column(db.String(100), nullable=False)
	time_in = db.Column(db.DateTime(), nullable=False)
	time_out = db.Column(db.DateTime(), nullable=True)
	tag_no = db.Column(db.String(50), nullable=True)
	
	def __init__(self, guest_name, host_name, host_email, host_slackid, purpose, time_in, time_out=None, tag_no=None):
		self.guest_name = guest_name
		self.host_name = host_name
		self.host_email = host_email
		self.host_slackid = host_slackid
		self.purpose = purpose
		self.time_in = time_in
		self.time_out = time_out
		self.tag_no = tag_no
