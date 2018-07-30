from .base_controller import BaseController, make_response
from app.repositories import GuestRepo
from app.utils import timestring_to_datetime
from threading import Thread
import requests
import json


class BotController(BaseController):
	
	def __init__(self, request):
		BaseController.__init__(self, request)
		self.request_slack_id = request.data.get('user_id')
		self.message_trigger = request.data.get('trigger_id')
		self.guest_repo = GuestRepo()
		
		if self.request_slack_id is not None:
			self.slack_user_info = self.slackhelper.user_info(self.request_slack_id)
		
		self.dialog_element = [
			{
				"label": "Guest Name",
				"type": "text",
				"name": "guest_name",
				"placeholder": "Person McAwesome",
			},
			{
				"label": "Purpose of Visit",
				"type": "select",
				"name": "purpose",
				"options": [
					{
						"label": "Personal",
						"value": "personal"
					},
					{
						"label": "Official",
						"value": "official"
					},
				]
			},
			{
				"label": "Expected Arrival Time",
				"type": "text",
				"name": "time_in",
				"placeholder": "eg 08:00, 15:33",
				"hint": "What time today is your guest coming in? - 12hr or 24hr format WITHOUT AM or PM.",
			},
		]
		
	def handle(self):
		# Switch To Backgroud Thread To Avoid Slack Timeout
		
		thr = Thread(target=self.create_dialog)
		thr.start()
		
		return self.handle_response(slack_response={'text': 'Registering Your Guest - Please Wait'})
	
	def create_dialog(self):
		dialog = {
			"title": "Register Guest",
			"submit_label": "Register",
			"callback_id": "register_guest",
			"notify_on_cancel": True,
			"elements": self.dialog_element
		}
		self.slackhelper.dialog(dialog=dialog, trigger_id=self.message_trigger)
		
	def interaction(self):
		request_payload = json.loads(self.request.data.get('payload'))
		webhook_url = request_payload["response_url"]
		slack_id = request_payload['user']['id']
		
		slack_user_info = self.slackhelper.user_info(slack_id)
		user_data = slack_user_info['user']
		
		if request_payload['type'] == "dialog_submission":
			
			guest_name = request_payload['submission']['guest_name']
			purpose = request_payload['submission']['purpose']
			time_in = timestring_to_datetime(request_payload['submission']['time_in'])
	
			if time_in is None:
				return self.handle_response(slack_response={'errors': [{'name': 'time_in', 'error': 'Invalid Time Format Supplied'}]})
			
			self.guest_repo.new_guest(guest_name=guest_name, host_name=user_data['real_name'], host_email=user_data['profile']['email'], host_slackid=slack_id, purpose=purpose, time_in=time_in)
			slack_data = {'text': "I've added {} to your guest list. I'd notify you when they get to the reception.".format(guest_name)}
			requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
			
			return make_response('', 200)

		elif request_payload['type'] == 'dialog_cancellation':
			slack_data = {'text': "Cool! - I've canceled the process."}
			requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

