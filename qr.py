# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import base64
# import cv2
# import numpy as np
# from ultralytics import YOLO
# from paddleocr import PaddleOCR
# import qrcode
# from io import BytesIO
# import base64

# app = Flask(__name__)
# CORS(app)

# # Load YOLO model (your custom trained best.pt)
# model = YOLO("best.pt")  
# ocr = PaddleOCR(use_angle_cls=True, lang="en")  # OCR model

# def decode_image(image_data):
#     """ Convert base64 image to OpenCV format """
#     try:
#         img_bytes = base64.b64decode(image_data.split(',')[1])
#         nparr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         return img
#     except Exception as e:
#         print("Error decoding image:", e)
#         return None

# def generate_qr(data):
#     qr = qrcode.QRCode(version=1, box_size=10, border=2)
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill="black", back_color="white")
#     buffered = BytesIO()
#     img.save(buffered, format="PNG")
#     qr_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
#     return "data:image/png;base64," + qr_b64

# @app.route('/detect', methods=['POST'])
# def detect():
#     try:
#         data = request.get_json()
#         image_data = data.get("image")
#         if not image_data:
#             return jsonify({"error": "No image provided"}), 400

#         # Decode base64 image to OpenCV image
#         img = decode_image(image_data)
#         if img is None:
#             return jsonify({"error": "Invalid image format"}), 400

#         # Run YOLO detection
#         results = model(img)
#         detected_text = None

#         # Loop over detected boxes and run OCR on each cropped plate
#         for result in results:
#             boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
#             for box in boxes:
#                 x1, y1, x2, y2 = map(int, box)
#                 cropped_plate = img[y1:y2, x1:x2]
#                 if cropped_plate.size == 0:
#                     continue

#                 ocr_result = ocr.ocr(cropped_plate, cls=True)
#                 # Concatenate all detected words for the plate
#                 detected_text = " ".join([word_info[1][0] for line in ocr_result for word_info in line])
#                 break  # Use first detected plate only
#             if detected_text:
#                 break

#         if not detected_text:
#             detected_text = "No Number Plate Detected"

#         # Generate QR code with detected number plate text (or error message)
#         qr_image = generate_qr(detected_text)

#         return jsonify({
#             "number_plate": detected_text,
#             "qr_image": qr_image
#         })

#     except Exception as e:
#         print("Error:", e)
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import base64
# import cv2
# import numpy as np
# from ultralytics import YOLO
# from paddleocr import PaddleOCR
# import qrcode
# from io import BytesIO
# import datetime
# from pymongo import MongoClient

# app = Flask(__name__)
# CORS(app)
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# # Initialize models
# model = YOLO("best.pt")
# ocr = PaddleOCR(use_angle_cls=True, lang="en")

# # MongoDB setup
# client = MongoClient("mongodb+srv://suryateja2neti:Suryateja@parksense.coocf1i.mongodb.net/")
# db = client["parksense"]
# qr_collection = db["qr_codes"]

# def decode_image(image_data):
#     try:
#         if ',' in image_data:
#             img_bytes = base64.b64decode(image_data.split(',')[1])
#         else:
#             img_bytes = base64.b64decode(image_data)
#         nparr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         return img
#     except Exception as e:
#         print("Error decoding image:", e)
#         return None

# def generate_qr(data):
#     qr = qrcode.QRCode(version=1, box_size=10, border=2)
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill="black", back_color="white")
#     buffered = BytesIO()
#     img.save(buffered, format="PNG")
#     qr_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
#     return "data:image/png;base64," + qr_b64

# @app.route('/detect', methods=['POST'])
# def detect():
#     try:
#         data = request.get_json()
#         if not data or 'image' not in data:
#             return jsonify({"error": "No image provided"}), 400

#         image_data = data['image']
#         if len(image_data) > 10 * 1024 * 1024:  # 10MB
#             return jsonify({"error": "Image too large (max 10MB)"}), 413

#         img = decode_image(image_data)
#         if img is None:
#             return jsonify({"error": "Invalid image format"}), 400

#         # Run detection
#         results = model(img)
#         detected_text = None

#         for result in results:
#             boxes = result.boxes.xyxy.cpu().numpy()
#             for box in boxes:
#                 x1, y1, x2, y2 = map(int, box)
#                 cropped_plate = img[y1:y2, x1:x2]
#                 if cropped_plate.size == 0:
#                     continue
                
#                 ocr_result = ocr.ocr(cropped_plate, cls=True)
#                 detected_text = " ".join([word_info[1][0] for line in ocr_result for word_info in line]).replace(" ", "")
#                 break
#             if detected_text:
#                 break

#         if not detected_text:
#             detected_text = "NoNumberPlateDetected"

#         # Generate QR code
#         base_url = "http://172.168.0.152:5173/entry/"
#         qr_data = base_url + detected_text
#         qr_image = generate_qr(qr_data)

#         # Store in MongoDB
#         qr_collection.update_one(
#             {"plate_number": detected_text},
#             {
#                 "$set": {
#                     "plate_number": detected_text,
#                     "qr_image": qr_image,
#                     "created_at": datetime.datetime.utcnow()
#                 }
#             },
#             upsert=True
#         )

#         return jsonify({
#             "number_plate": detected_text,
#             "qr_image": qr_image
#         })

#     except Exception as e:
#         print("Server error:", e)
#         return jsonify({"error": "Internal server error"}), 500

# @app.route('/get-qr', methods=['GET'])
# def get_qr():
#     try:
#         plate_number = request.args.get("plate_number")
#         if not plate_number:
#             return jsonify({"error": "Missing plate_number"}), 400

#         record = qr_collection.find_one({"plate_number": plate_number})
#         if not record:
#             return jsonify({"error": "QR not found"}), 404

#         return jsonify({
#             "plate_number": record["plate_number"],
#             "qr_image": record["qr_image"]
#         })

#     except Exception as e:
#         print("Error retrieving QR:", e)
#         return jsonify({"error": "Database error"}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
import qrcode
from io import BytesIO
import datetime
from pymongo import MongoClient

app = Flask(__name__)
# Configure CORS to allow your frontend URLs
CORS(app, resources={
    r"/detect": {"origins": ["http://localhost:5173", "http://172.168.0.152:5173" , "http://192.168.1.37:5173"]},
    r"/get-qr": {"origins": {"origins": "*"}}
})
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Initialize models
model = YOLO("best.pt")
ocr = PaddleOCR(use_angle_cls=True, lang="en")

# MongoDB setup
client = MongoClient("mongodb+srv://suryateja2neti:Suryateja@parksense.coocf1i.mongodb.net/")
db = client["parksense"]
qr_collection = db["qr_codes"]

def decode_image(image_data):
    try:
        if ',' in image_data:
            img_bytes = base64.b64decode(image_data.split(',')[1])
        else:
            img_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print("Error decoding image:", e)
        return None

def generate_qr(data):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{img_str}"

@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image provided"}), 400

        image_data = data['image']
        if len(image_data) > 10 * 1024 * 1024:  # 10MB
            return jsonify({"error": "Image too large (max 10MB)"}), 413

        img = decode_image(image_data)
        if img is None:
            return jsonify({"error": "Invalid image format"}), 400

        # Run detection
        results = model(img)
        detected_text = None

        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cropped_plate = img[y1:y2, x1:x2]
                if cropped_plate.size == 0:
                    continue
                
                ocr_result = ocr.ocr(cropped_plate, cls=True)
                detected_text = " ".join([word_info[1][0] for line in ocr_result for word_info in line]).replace(" ", "")
                break
            if detected_text:
                break

        if not detected_text:
            detected_text = "NoNumberPlateDetected"

        # Generate QR code - Use your computer's IP for local testing
        base_url = "http://192.168.1.37:5173/entry/"
        qr_data = base_url + detected_text
        qr_image = generate_qr(qr_data)

        # Store in MongoDB
        qr_collection.update_one(
            {"plate_number": detected_text},
            {
                "$set": {
                    "plate_number": detected_text,
                    "qr_image": qr_image,
                    "created_at": datetime.datetime.utcnow()
                }
            },
            upsert=True
        )

        return jsonify({
            "number_plate": detected_text,
            "qr_image": qr_image
        })

    except Exception as e:
        print("Server error:", e)
        return jsonify({"error": "Internal server error"}), 500
@app.route('/get-qr', methods=['GET'])
def get_qr():
    try:
        plate_number = request.args.get("plate_number")
        print(f"Received plate_number: {plate_number}")  # Debug log
        if not plate_number:
            return jsonify({"error": "Missing plate_number"}), 400

        # Check if QR exists in DB
        record = qr_collection.find_one({"plate_number": plate_number})
        print(f"Database record: {record}")  # Debug log
        if record:
            return jsonify({
                "plate_number": record["plate_number"],
                "qr_image": record["qr_image"]
            })

        # Handle special guest case
        if plate_number == "NONUMBERPLATEDETECTED":
            base_url = "http://192.168.1.37:5173/entry/"
            qr_data = base_url + "guest"
            qr_image = generate_qr(qr_data)

            qr_collection.update_one(
                {"plate_number": "guest"},
                {"$set": {"qr_image": qr_image}},
                upsert=True
            )

            return jsonify({
                "plate_number": "guest",
                "qr_image": qr_image
            })

        # Generate new QR if not found
        base_url = "http://192.168.1.37:5173/entry/"
        qr_data = base_url + plate_number
        qr_image = generate_qr(qr_data)

        qr_collection.update_one(
            {"plate_number": plate_number},
            {"$set": {"qr_image": qr_image}},
            upsert=True
        )

        return jsonify({
            "plate_number": plate_number,
            "qr_image": qr_image
        })

    except Exception as e:
        print(f"Error in /get-qr: {str(e)}")  # Detailed error log
        return jsonify({"error": f"Database error: {str(e)}"}), 500
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)