from slackclient import SlackClient
from config import get_env


class SlackHelper:

	def __init__(self):
		self.slack_token = get_env('SLACK_TOKEN')
		self.slack_client = SlackClient(self.slack_token)

	def post_message(self, msg, recipient, attachments=None):
		return self.slack_client.api_call(
			"chat.postMessage",
			channel=recipient,
			text=msg,
			attachments=attachments,
			as_user=True
		)

	def update_message(self, msg, recipient, message_ts=None, attachments=None):
		return self.slack_client.api_call(
			"chat.update",
			channel=recipient,
			ts=message_ts,
			text=msg,
			attachments=attachments,
			as_user=True
		)

	def user_info(self, uid):
		return self.slack_client.api_call(
			"users.info",
			user=uid,
			token=self.slack_token
		)

	def dialog(self, dialog, trigger_id):
		return self.slack_client.api_call("dialog.open", trigger_id=trigger_id, dialog=dialog)
