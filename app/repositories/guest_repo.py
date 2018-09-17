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
			return Guest.query.filter_by(host_email=host_email).order_by(Guest.created_at.desc()).paginate(error_out=False, per_page=50)
		else:
			return Guest.query.order_by(Guest.created_at.desc()).paginate(error_out=False, per_page=50)
	
	@staticmethod
	def new_guest(guest_name, host_name, host_email, host_slackid, purpose, location, time_in, time_out=None, tag_no=None, group_size=1):
		guest = Guest(
			guest_name=guest_name, host_name=host_name, host_email=host_email, host_slackid=host_slackid, purpose=purpose,
			location=location, time_in=time_in, time_out=time_out, tag_no=tag_no, group_size=group_size)
		guest.save()
		return guest
