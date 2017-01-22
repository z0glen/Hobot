from marshmallow import Schema, fields, pprint
from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
import os

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = 'secretkey'

db = SQLAlchemy(app)
api = Api(app)

class UserMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(120), unique=False)
    response = db.Column(db.String(120), unique=False)
	
    def __init__(self, message, response):
        self.message = message
        self.response = response

    def __repr__(self):
        return '<UserMessage %r>' % self.message	

class UserMessageSchema(Schema):
	message = fields.Str()
	response = fields.Str()
	
class GetMessages(Resource):
	def get(self):
		schema = UserMessageSchema(many=True)
		json_result = schema.dump(UserMessage.query.all())
		pprint(json_result.data)
		return json_result
	
api.add_resource(GetMessages, '/getmessages')

@app.route('/')
def show_all():
	return render_template('show_all.html', messages = UserMessage.query.all())

if __name__ == '__main__':
   db.create_all()
   app.run(debug = True)
