import time
import logging
from flask import Flask, request, render_template, send_file, jsonify
import cv2
import os
from weapon_detection import WeaponDetectionSystem  

app = Flask(__name__)
detector = WeaponDetectionSystem(model_size='m')
detector.load_model('static/models/best.pt')

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/health")
def health():
    return "OK", 200

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        # Ensure the uploads directory exists
        uploads_dir = os.path.join('static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        image_path = os.path.join(uploads_dir, file.filename)
        file.save(image_path)
        
        start_time = time.time()
        preprocess_time = time.time()
        try:
            annotated_image, detections = detector.detect(image_path)
        except Exception as e:
            app.logger.error(f"Detection error: {str(e)}")
            return jsonify({"error": "Detection failed"}), 500
        
        inference_time = time.time() - preprocess_time
        postprocess_time = time.time() - start_time - inference_time
        total_time = time.time() - start_time
        
        if annotated_image is not None:
            output_path = os.path.join('static/annotated_images', file.filename)
            cv2.imwrite(output_path, annotated_image)
            
            height, width = annotated_image.shape[:2]
            weapon_count = sum(1 for d in detections if d['class'] == 'Weapon')
            
            stats = (
                f"0: {width}x{height} {weapon_count} weapon, {total_time*1000:.1f}ms\n"
                f"Speed: {preprocess_time*1000:.1f}ms preprocess, {inference_time*1000:.1f}ms inference, "
                f"{postprocess_time*1000:.1f}ms postprocess per image at shape (1, 3, {width}, {height})"
            )
            
            return jsonify({
                "image_url": f"/static/annotated_images/{file.filename}",
                "stats": stats
            })
        else:
            return jsonify({"error": "Detection failed"}), 500
    return jsonify({"error": "File upload failed"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)