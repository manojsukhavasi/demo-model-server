# Flask API server for badminton and Tennis

##Requirements:
- Flask
- Flask_restful
- Redis `sudo apt-get install redis-server` , `pip install redis`
- Celery `pip install celery`
- AlphaPose


## Running the server
TODO: Need to update the server to production server
- Flask - `MAIL= PASSWORD= python app.py`
- Redis - `redis-server`
- Celery - `MAIL= PASSWORD= celery worker -A app.celery --loglevel=info --concurrency=1`