from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import pickle
import numpy as np
import redis
from celery import Celery

from utils.send_mail import send_mail
from utils.gcp_utils import copy_to_bucket

from badminton.badminton_demo import get_badminton_highlights
from tennis.tennis_demo import get_tennis_highlights


app = Flask(__name__)

db = redis.StrictRedis(host="localhost", port=6379, db=0)



# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


api = Api(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def process_badminton_video(args):
    id = get_badminton_highlights(args['url'])
    file_link = f'./results/run_{id}/output.zip'
    public_url = copy_to_bucket(f'{id}.zip', file_link, 'badminton')
    send_mail(args['email'], public_url)

@celery.task
def process_tennis_video(args):
    id = get_tennis_highlights(args['url'])
    file_link = f'./results/run_{id}/output.zip'
    public_url = copy_to_bucket(f'{id}.zip', file_link, 'tennis')
    send_mail(args['email'], public_url)


# argument parsing
parser = reqparse.RequestParser()
parser.add_argument('url')
parser.add_argument('email')


class GetBadmintonHighlights(Resource):
    def get(self):
        args = parser.parse_args()
        process_badminton_video.delay(args)
        return "Finished"

class GetTennisHighlights(Resource):
    def get(self):
        args = parser.parse_args()
        process_tennis_video.delay(args)
        return "Finished"


# Setup the Api resource routing here
# Route the URL to the resource
api.add_resource(GetBadmintonHighlights, '/badminton')
api.add_resource(GetTennisHighlights, '/tennis')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)