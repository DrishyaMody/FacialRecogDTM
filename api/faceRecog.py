from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from PIL import Image
from io import BytesIO
import base64

from api.jwt_authorize import token_required  # Needed for @token_required
from model.user import User                   # Needed for current_user methods

facial_api = Blueprint('facial_api', __name__, url_prefix='/facial')
api = Api(facial_api)

# --- Mock Facial Recognition Logic ---
def mock_facial_recognition(image: Image.Image) -> bool:
    # Placeholder: Always returns True
    return True


# --- Register a user's facial image ---
class FacialRegister(Resource):
    @token_required()
    def post(self):
        try:
            current_user = g.current_user  # Populated from JWT decorator
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


# --- Login using facial recognition ---
class FacialLogin(Resource):
    @token_required()
    def post(self):
        try:
            current_user = g.current_user
            data = request.get_json()

            if not data or 'image' not in data:
                return jsonify({'success': False, 'message': 'No image provided'}), 400

            image_data = data['image'].split(",")[1]
            image_bytes = base64.b64decode(image_data)

            # --- Placeholder for actual face recognition
            recognized = True  # Replace with real logic

            if recognized:
                return jsonify({
                    'success': True,
                    'message': 'Face recognized',
                    'user': current_user.read()  # Full user data!
                })
            else:
                return jsonify({'success': False, 'message': 'Face not recognized'})
        except Exception as e:
            print("Facial login error:", e)
            return jsonify({'success': False, 'message': 'Error processing image'}), 500
        
# --- Register the resources with the API ---
api.add_resource(FacialLogin, '/login')
api.add_resource(FacialRegister, '/register')
