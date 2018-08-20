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
				"label": "Person or Group Name",
				"type": "text",
				"name": "guest_name",
				"placeholder": "Person McAwesome",
			},
			{
				"label": "Group Size",
				"type": "text",
				"name": "group_size",
				"placeholder": "",
				"value": "1",
				"hint": "Number of guests expected. Defaults to 1",
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
				"label": "Expected Time In",
				"type": "text",
				"name": "time_in",
				"placeholder": "eg 08:00, 15:33",
				"hint": "What time is your guest coming in? - 24hr format WITHOUT AM or PM.",
			},
			{
				"label": "Estimated Time Out",
				"type": "text",
				"name": "time_out",
				"placeholder": "eg 08:00, 15:33",
				"hint": "24hr format WITHOUT AM or PM.",
			}
		]
		
		self.location_buttons = [
				{
					"text": "Select Location",
					"callback_id": "host_location",
					"color": "#3AA3E3",
					"attachment_type": "default",
					"actions": [
						{
							"name": "location",
							"text": "Lagos",
							"type": "button",
							"value": 'lagos',
							"style": "primary",
						},
						{
							"name": "location",
							"text": "Nairobi",
							"type": "button",
							"value": "nairobi"
						},
						{
							"name": "location",
							"text": "Kampala",
							"type": "button",
							"value": "kampala"
						},
						{
							"name": "location",
							"text": "New York",
							"type": "button",
							"value": "new-york"
						},
						{
							"name": "location",
							"text": "Kigali",
							"type": "button",
							"value": "kigali"
						},
					]
				}
			]
		
	def handle(self):
		# Prompt User to Select Location
		return self.handle_response(slack_response={'text': '', 'attachments': self.location_buttons})
	
	def create_dialog(self, location, trigger_id):
		dialog = {
			"title": "Register Guest",
			"submit_label": "Register",
			"callback_id": "register_guest_{}".format(location),
			"notify_on_cancel": True,
			"elements": self.dialog_element
		}
		return self.slackhelper.dialog(dialog=dialog, trigger_id=trigger_id)
	
	def prompt_location(self):
		self.slackhelper.post_message(msg='Open the guesty app', recipient=self.request_slack_id, attachments=self.location_buttons)
		
	def interaction(self):
		request_payload = json.loads(self.request.data.get('payload'))
		
		print(request_payload)
		
		webhook_url = request_payload["response_url"]
		slack_id = request_payload['user']['id']
		
		slack_user_info = self.slackhelper.user_info(slack_id)
		user_data = slack_user_info['user']
		
		if request_payload['type'] == "dialog_submission":
			
			guest_name = request_payload['submission']['guest_name']
			purpose = request_payload['submission']['purpose']
			time_in = timestring_to_datetime(request_payload['submission']['time_in'])
			time_out = timestring_to_datetime(request_payload['submission']['time_out'])
			group_size = request_payload['submission']['group_size']
			location = request_payload['callback_id'].split('_')[2]
	
			if time_in is None:
				return self.handle_response(slack_response={'errors': [{'name': 'time_in', 'error': 'Invalid Time Format Supplied'}]})
			
			if time_out is None:
				return self.handle_response(slack_response={'errors': [{'name': 'time_out', 'error': 'Invalid Time Format Supplied'}]})
			
			if time_out.time() <= time_in.time():
				return self.handle_response(slack_response={'errors': [{'name': 'time_out', 'error': 'Time out must be ahead of Time in'}]})
			
			if int(group_size) < 1:
				return self.handle_response(slack_response={'errors': [{'name': 'group_size', 'error': 'Invalid Guest Size Supplied'}]})
			
			r = self.guest_repo.new_guest(
				guest_name=guest_name,
				host_name=user_data['real_name'],
				host_email=user_data['profile']['email'],
				host_slackid=slack_id,
				purpose=purpose,
				location=location,
				time_in=time_in,
				time_out=time_out,
				group_size=group_size)
			
			slack_data = {'text': "I've added {} to your guest list. I'd notify you when they get to the reception.".format(guest_name)}
			requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
		
		if request_payload['type'] == "interactive_message" and request_payload['callback_id'] == 'host_location':
			payload_action_name = request_payload['actions'][0]['name']
			payload_action_value = request_payload['actions'][0]['value']
			self.create_dialog(location=payload_action_value, trigger_id=request_payload['trigger_id'])
			return self.handle_response(slack_response={'text': 'Adding Your Guest To {} Guest Book'.format(payload_action_value)})
			
		elif request_payload['type'] == 'dialog_cancellation':
			slack_data = {'text': "Cool! - I've canceled the process."}
			requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
		
		return make_response('', 200)

