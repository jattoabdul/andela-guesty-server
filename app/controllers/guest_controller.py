from .base_controller import BaseController
from app.repositories import GuestRepo
from app.utils import timestring_to_datetime, time_format_12_24


class GuestController(BaseController):
	
	def __init__(self, request):
		BaseController.__init__(self, request)
		self.repo = GuestRepo
		
	def list_guests(self):
		host_email = self.request.args.get('host_email')
		guests = self.repo.list_guests(host_email=host_email)
		guest_list = [{'id': guest.id, 'guest_name': guest.guest_name, 'host_name': guest.host_name, 'host_email': guest.host_email, 'purpose': guest.purpose, 'time_in': time_format_12_24(guest.time_in), 'time_out': time_format_12_24(guest.time_out), 'tag_no': guest.tag_no, 'timestamps': self.prettify_response_dates(created_at=guest.created_at, updated_at=guest.updated_at)} for guest in guests.items]
		
		return self.handle_response(msg='OK', payload={'guests': guest_list, 'meta': self.pagination_meta(guests)})
	
	def new_guest(self):
		guest_name = self.request.data.get('guest_name')
		host_email = self.request.data.get('host_email')
		purpose = self.request.data.get('purpose')
		time_in = self.request.data.get('time_in')
		time_out = self.request.data.get('time_out')
		tag_no = self.request.data.get('tag_no')
		
		host_info = self.slackhelper.find_by_email(host_email)
		if host_info['ok'] is True:
			host_slackid = host_info['user']['id']
			host_name = host_info['user']['real_name']
			
			if self.missing_required([guest_name, host_name, host_email, purpose, time_in]):
				return self.missing_response()
			
			time_in = timestring_to_datetime(time_in)
			time_out = timestring_to_datetime(time_out) if time_out is not None else None
			
			guest = self.repo.new_guest(guest_name=guest_name, host_name=host_name, host_email=host_email, host_slackid=host_slackid, purpose=purpose, time_in=time_in, time_out=time_out, tag_no=tag_no)
			if guest:
				payload = {'id': guest.id, 'guest_name': guest.guest_name, 'host_name': guest.host_name, 'host_email': guest.host_email, 'purpose': guest.purpose, 'time_in': time_format_12_24(guest.time_in), 'time_out': time_format_12_24(guest.time_out), 'tag_no': guest.tag_no, 'timestamps': self.prettify_response_dates(created_at=guest.created_at, updated_at=guest.updated_at)}
				return self.handle_response(msg='OK', payload=payload)
			else:
				return self.handle_response(msg='Application Error', status_code=500)
		else:
			return self.handle_response(msg='No User Found With That Email Address', status_code=400)

	def update_guest(self, guest_id, field):
		guest = self.repo.find_by_id(guest_id)
		tag_no = self.request.data.get('tag_no')
		time_out = self.request.data.get('time_out')
		beep = self.request.data.get('beep')
		
		if not guest:
			return self.handle_response(msg='Invalid or Incorrect Guest ID', status_code=400)
		else:
			
			if field == 'tag':
				if self.missing_required([tag_no]):
					return self.missing_response()
				guest.tag_no = tag_no
				
			if field == 'time-out':
				if self.missing_required([time_out]):
					return self.missing_response()
				guest.time_out = timestring_to_datetime(time_out)
				
			guest.save()
			
			if beep:
				pass
			
			payload = {'id': guest.id, 'guest_name': guest.guest_name, 'host_name': guest.host_name, 'host_email': guest.host_email, 'purpose': guest.purpose, 'time_in': time_format_12_24(guest.time_in), 'time_out': time_format_12_24(guest.time_out), 'tag_no': guest.tag_no}
			return self.handle_response(msg='OK', payload=payload)
