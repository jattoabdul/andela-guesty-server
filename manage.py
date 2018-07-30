from flask_script import Manager
from flask import request
from flask_migrate import Migrate, MigrateCommand
from app import create_app, controllers
from app.utils import db
from config import get_env


app = create_app(get_env('APP_ENV'))
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route('/api/v1/guests', methods=['GET'])
def list_guests():
	guest_controller = controllers.GuestController(request)
	return guest_controller.list_guests()


@app.route('/api/v1/guest', methods=['POST'])
def new_guest():
	guest_controller = controllers.GuestController(request)
	return guest_controller.new_guest()


@app.route('/api/v1/guest/<int:guest_id>/update/<string:field>', methods=['PATCH', 'PUT'])
def update_guest(guest_id, field):
	guest_controller = controllers.GuestController(request)
	return guest_controller.update_guest(guest_id, field)


@app.route('/api/v1/slack-bot', methods=['POST'])
def slack_bot():
	bot_controller = controllers.BotController(request)
	return bot_controller.handle()


@app.route('/api/v1/slack-interaction', methods=['POST'])
def slack_interaction():
	bot_controller = controllers.BotController(request)
	return bot_controller.interaction()


if __name__ == '__main__':
	manager.run()
