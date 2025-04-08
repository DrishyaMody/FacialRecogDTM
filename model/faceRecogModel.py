# import face_recognition
# import numpy as np
# import os

# class FaceRecognitionModel:
#     def __init__(self, known_faces_dir: str):
#         self.known_face_encodings = []
#         self.known_face_names = []
#         self.load_known_faces(known_faces_dir)

#     def load_known_faces(self, known_faces_dir):
#         for filename in os.listdir(known_faces_dir):
#             if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
#                 path = os.path.join(known_faces_dir, filename)
#                 image = face_recognition.load_image_file(path)
#                 encodings = face_recognition.face_encodings(image)
#                 if encodings:
#                     self.known_face_encodings.append(encodings[0])
#                     self.known_face_names.append(os.path.splitext(filename)[0])

#     def recognize_faces(self, frame: np.ndarray, scale=0.25):
#         small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
#         rgb_small_frame = small_frame[:, :, ::-1]

#         locations = face_recognition.face_locations(rgb_small_frame)
#         encodings = face_recognition.face_encodings(rgb_small_frame, locations)

#         names = []
#         for encoding in encodings:
#             matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
#             name = "Unknown"
#             distances = face_recognition.face_distance(self.known_face_encodings, encoding)
#             if distances.size > 0:
#                 best_match = np.argmin(distances)
#                 if matches[best_match]:
#                     name = self.known_face_names[best_match]
#             names.append(name)

#         # Scale locations back to original size
#         scaled_locations = [(top // scale, right // scale, bottom // scale, left // scale)
#                             for top, right, bottom, left in locations]

#         return scaled_locations, names
