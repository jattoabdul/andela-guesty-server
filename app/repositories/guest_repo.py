from app.models.guest import Guest


class GuestRepo:
	
	@staticmethod
	def find_by_id(id):
		return Guest.query.filter_by(id=id).first()
	
	@staticmethod
	def find_by_tag_no(tag_no):
		return Guest.query.filter_by(tag_no=tag_no).paginate(error_out=False)
	
	@staticmethod
	def find_by_host_email(host_email):
		return Guest.query.filter_by(host_email=host_email).paginate(error_out=False)
	
	@staticmethod
	def all():
		return Guest.query.paginate(error_out=False)
	
	@staticmethod
	def list_guests(host_email=None):
		if host_email:
			return Guest.query.filter_by(host_email=host_email).order_by(Guest.created_at.desc()).paginate(error_out=False)
		else:
			return Guest.query.paginate(error_out=False)
	
	@staticmethod
	def new_guest(guest_name, host_name, host_email, host_slackid, purpose, time_in, time_out=None, tag_no=None):
		guest = Guest(guest_name=guest_name, host_name=host_name, host_email=host_email, host_slackid=host_slackid, purpose=purpose, time_in=time_in, time_out=time_out, tag_no=tag_no)
		guest.save()
		return guest
