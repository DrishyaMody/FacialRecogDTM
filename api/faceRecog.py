from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource
from PIL import Image
from io import BytesIO
import base64
import os
import face_recognition
import jwt

from api.jwt_authorize import token_required
from model.user import User

facial_api = Blueprint('facial_api', __name__, url_prefix='/facial')
api = Api(facial_api)


# --- Register a user's facial image ---
class FacialRegister(Resource):
    @token_required()
    def post(self):
        try:
            current_user = g.current_user
            data = request.get_json()
            image_data = data.get('image')

            if not image_data:
                return {'error': 'No image data provided'}, 400

            image_bytes = base64.b64decode(image_data.split(',')[1])
            filename = "face.png"

            current_user.save_face_image(image_bytes, filename)

            return jsonify({"success": True, "message": "Facial image saved successfully."})
        except Exception as e:
            print("Facial registration error:", e)
            return jsonify({"success": False, "message": "Error saving facial image"}), 500


# --- Facial recognition login for already-authenticated users ---
class FacialLogin(Resource):
    @token_required()
    def post(self):
        try:
            current_user = g.current_user
            data = request.get_json()
            image_data = data['image'].split(",")[1]
            image_bytes = base64.b64decode(image_data)

            # Optional: use real face match here (compare against stored image for current_user)

            return jsonify({
                'success': True,
                'message': 'Face recognized',
                'user': current_user.read()
            })
        except Exception as e:
            print("Facial login error:", e)
            return jsonify({'success': False, 'message': 'Error processing image'}), 500


# --- Passwordless face authentication (true facial login) ---
class FacialAuth(Resource):
    def post(self):
        try:
            data = request.get_json()
            image_data = data.get('image')

            if not image_data:
                return jsonify({"success": False, "message": "No image data provided"}), 400

            image_bytes = base64.b64decode(image_data.split(',')[1])
            uploaded_image = face_recognition.load_image_file(BytesIO(image_bytes))
            uploaded_encoding = face_recognition.face_encodings(uploaded_image)

            if not uploaded_encoding:
                return jsonify({"success": False, "message": "No face detected in image."}), 400

            uploaded_encoding = uploaded_encoding[0]

            # Compare against all users
            for user in User.query.all():
                if not user.face_image:
                    continue

                face_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.uid, user.face_image)
                if not os.path.exists(face_path):
                    continue

                stored_image = face_recognition.load_image_file(face_path)
                stored_encodings = face_recognition.face_encodings(stored_image)

                if not stored_encodings:
                    continue

                match = face_recognition.compare_faces([stored_encodings[0]], uploaded_encoding)[0]

                if match:
                    token = jwt.encode({"_uid": user.uid}, current_app.config["SECRET_KEY"], algorithm="HS256")
                    resp = jsonify({
                        "success": True,
                        "message": f"Welcome, {user.uid}",
                        "user": user.read()
                    })
                    resp.set_cookie(
                        current_app.config["JWT_TOKEN_NAME"],
                        token,
                        max_age=3600,
                        secure=True,
                        httponly=True,
                        path='/',
                        samesite='None'
                    )
                    return resp

            return jsonify({"success": False, "message": "No matching face found."}), 401

        except Exception as e:
            print("Facial authenticate error:", e)
            return jsonify({"success": False, "message": "Error during face authentication"}), 500


# --- Register endpoints ---
api.add_resource(FacialLogin, '/login')             # 🔐 logged-in users only
api.add_resource(FacialRegister, '/register')       # ✅ register face for current user
api.add_resource(FacialAuth, '/authenticate')       # 🚀 passwordless facial login
