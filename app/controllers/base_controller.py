from flask import jsonify, make_response
from app.utils import datetime, slackhelper


class BaseController:
	
	def __init__(self, request):
		self.request = request
		self.slackhelper = slackhelper
	
	def handle_response(self, msg='OK', payload=None, status_code=200, slack_response=None):
		
		# If there is no specific slack formatted response, default to WEB API Response format
		if slack_response is None:
			data = {'msg': msg}
			if payload is not None:
				data['payload'] = payload
		else:
			data = slack_response
			
		response = jsonify(data)
		response.status_code = status_code
		return response
	
	def missing_required(self, params):
		return True if None in params or '' in params else False
	
	def missing_response(self, msg='Missing Required Parameters'):
		return self.handle_response(msg=msg, status_code=400)
	
	def pagination_meta(self, paginator):
		return {'total_rows': paginator.total, 'total_pages': paginator.pages, 'current_page': paginator.page,
				'next_page': paginator.next_num, 'prev_page': paginator.prev_num}
	
	def prettify_response_dates(self, created_at, updated_at=None):
		return {'created_at': created_at, 'updated_at': updated_at,
				'date_pretty_short': created_at.strftime('%b %d, %Y'), 'date_pretty': created_at.strftime('%B %d, %Y')}