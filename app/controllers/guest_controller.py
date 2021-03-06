import csv, os.path
from flask import send_file
from datetime import datetime
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
		guest_list = [{
			'id': guest.id, 'guest_name': guest.guest_name, 'host_name': guest.host_name, 'host_email': guest.host_email,
			'purpose': guest.purpose, 'location': guest.location, 'time_in': time_format_12_24(guest.time_in),
			'time_out': time_format_12_24(guest.time_out), 'tag_no': guest.tag_no, 'group_size': guest.group_size,
			'submit_tag': bool(guest.submit_tag), 'timestamps': self.prettify_response_dates(created_at=guest.created_at, updated_at=guest.updated_at)
		} for guest in guests.items]
		
		return self.handle_response(msg='OK', payload={'guests': guest_list, 'meta': self.pagination_meta(guests)})
	
	def new_guest(self):
		guest_name = self.request.data.get('guest_name')
		host_email = self.request.data.get('host_email')
		purpose = self.request.data.get('purpose')
		time_in = self.request.data.get('time_in')
		time_out = self.request.data.get('time_out')
		tag_no = self.request.data.get('tag_no')
		location = self.request.data.get('location')
		group_size = self.request.data.get('group_size')
		group_size = 1 if group_size is None else group_size
		
		host_info = self.slackhelper.find_by_email(host_email)
		if host_info['ok'] is True:
			host_slackid = host_info['user']['id']
			host_name = host_info['user']['real_name']
			
			if self.missing_required([guest_name, host_name, host_email, purpose, time_in]):
				return self.missing_response()
			
			time_in = timestring_to_datetime(time_in)
			time_out = timestring_to_datetime(time_out) if time_out is not None else None
			
			guest = self.repo.new_guest(
				guest_name=guest_name,
				host_name=host_name,
				host_email=host_email,
				host_slackid=host_slackid,
				purpose=purpose,
				location=location,
				time_in=time_in,
				time_out=time_out,
				tag_no=tag_no,
				group_size=group_size)
			if guest:
				payload = {
					'id': guest.id, 'guest_name': guest.guest_name, 'host_name': guest.host_name, 'host_email': guest.host_email,
					'purpose': guest.purpose, 'location': guest.location, 'time_in': time_format_12_24(guest.time_in),
					'time_out': time_format_12_24(guest.time_out), 'tag_no': guest.tag_no, 'group_size': guest.group_size,
					'submit_tag': bool(guest.submit_tag),
					'timestamps': self.prettify_response_dates(created_at=guest.created_at, updated_at=guest.updated_at)
				}
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
		submit_tag = self.request.data.get('submit_tag')
		
		if not guest:
			return self.handle_response(msg='Invalid or Incorrect Guest ID', status_code=400)
		else:
			
			if field == 'tag-no':
				if self.missing_required([tag_no]):
					return self.missing_response()
				guest.tag_no = tag_no
				
				if beep.lower() == 'true':
					msg = 'Psst! your guest ({}) has arrived at the guests’ waiting area.'.format(guest.guest_name)
					self.slackhelper.post_message(msg=msg, recipient=guest.host_slackid)
				
			if field == 'time-out':
				if self.missing_required([time_out]):
					return self.missing_response()
				guest.time_out = timestring_to_datetime(time_out)
				
				if submit_tag.lower() == 'true':
					guest.submit_tag = 1
				else:
					msg = 'Hey {}! Your guest ({}) forgot to return our tag(s). Please get in touch with them'.format(guest.host_name, guest.guest_name)
					self.slackhelper.post_message(msg=msg, recipient=guest.host_slackid)
				
			guest.save()
			
			payload = {
				'id': guest.id, 'guest_name': guest.guest_name, 'host_name': guest.host_name, 'host_email': guest.host_email,
				'purpose': guest.purpose, 'location': guest.location, 'time_in': time_format_12_24(guest.time_in),
				'time_out': time_format_12_24(guest.time_out), 'tag_no': guest.tag_no, 'group_size': guest.group_size,
				'submit_tag': bool(guest.submit_tag),
				'timestamps': self.prettify_response_dates(created_at=guest.created_at, updated_at=guest.updated_at)}
			return self.handle_response(msg='OK', payload=payload)
		
	@property
	def export_data(self):
		all_guests = self.repo.all(paginate=False)
		
		file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'report.csv')
		file_name = '{}.csv'.format(datetime.now().strftime('%Y-%m-%d-%H%M'))
		
		with open(file_path, mode='w') as report:
			fieldnames = ['id', 'group_size', 'guest_name', 'host_name', 'host_email', 'location', 'purpose',
						  'submit_tag', 'tag_no', 'time_in','time_in_iso', 'time_out','time_out_iso',
						  'created_at','updated_at']
			report_writer = csv.DictWriter(report, fieldnames=fieldnames)
			report_writer.writeheader()
			
			for guest in all_guests:
				report_writer.writerow({'id':guest.id, 'group_size':guest.group_size, 'guest_name': guest.guest_name,
										'host_name': guest.host_name, 'host_email': guest.host_email, 'location': guest.location,
										'purpose': guest.purpose, 'submit_tag': bool(guest.submit_tag), 'tag_no': guest.tag_no,
										'time_in': time_format_12_24(guest.time_in)['format_12'],
										'time_in_iso': guest.time_in,
										'time_out': time_format_12_24(guest.time_out)['format_12'],
										'time_out_iso': guest.time_out, 'created_at': guest.created_at,
										'updated_at': guest.updated_at })
		
		return send_file(file_path, as_attachment=True, attachment_filename=f'guesty-logs-{file_name}')
