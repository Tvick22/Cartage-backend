import jwt
import uuid
import json
import os
import boto3
from model.imageUpload import UploadStatus
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource  # used for REST API building
from datetime import datetime
from __init__ import app, db
from api.jwt_authorize import token_required
from model.imageUpload import ImageUpload

upload_api = Blueprint('upload', __name__, url_prefix='/api')

api = Api(upload_api)

UPLOAD_FOLDER="instance/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_filename(upload_id, filename):
    return f"{str(upload_id)}.{filename.rsplit('.', 1)[1]}"

class UploadAPI:
    class _CRUD(Resource):
        def post(self):
            if 'file' not in request.files:
                return {'error': 'No file part'}, 400

            file = request.files['file']

            post_id = request.form.get("post_id")

            uid = request.form.get("uid")

            if file.filename == '':
                return {'error': 'No selected file'}, 400
            
            if not allowed_file(file.filename):
                return {'error': 'Unsupported file extension'}, 400

            upload_id = uuid.uuid4()

            orginal_filename = file.filename

            file.filename = unique_filename(upload_id, file.filename)
            
            save_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(save_path)

            db_image = ImageUpload(str(upload_id), orginal_filename, uid, UploadStatus.PENDING, post_id)
            try:
                db.session.add(db_image)

                sqs = boto3.client("sqs", region_name='us-east-2')

                queue_url = os.environ["AWS_SQS_URL"]

                # Construct the JSON payload
                message_payload = {
                    "upload_id": str(upload_id)
                }

                # Convert the Python dict to a JSON string
                message_body = json.dumps(message_payload)

                # Send the message
                response = sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message_body
                )

                db.session.commit()
            except Exception as error:
                db.session.rollback()
                raise error

            return {'message': 'Image uploaded and saved successfully'}, 200

    api.add_resource(_CRUD, '/upload')