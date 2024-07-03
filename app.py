from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_cors import CORS
import cv2
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'imagefile1' not in request.files or 'imagefile2' not in request.files:
            return jsonify({"error": "No image files provided"}), 400

        imagefile1 = request.files['imagefile1']
        imagefile2 = request.files['imagefile2']

        if imagefile1.filename == '' or imagefile2.filename == '':
            return jsonify({"error": "No selected files"}), 400

        path1 = os.path.join(app.config['UPLOAD_FOLDER'], imagefile1.filename)
        path2 = os.path.join(app.config['UPLOAD_FOLDER'], imagefile2.filename)

        imagefile1.save(path1)
        imagefile2.save(path2)

        img1 = cv2.imread(path1)
        img2 = cv2.imread(path2)

        if img1 is None or img2 is None:
            if img1 is None:
                os.remove(path1)
            if img2 is None:
                os.remove(path2)
            return jsonify({"error": "Could not read one of the images"}), 400

        img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        alpha = 0.5
        beta = 0.5
        gamma = 0
        merged_image = cv2.addWeighted(img1, alpha, img2_resized, beta, gamma)

        output_filename = 'merged_image.jpg'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        cv2.imwrite(output_path, merged_image)

        os.remove(path1)
        os.remove(path2)

        return send_from_directory(app.config['OUTPUT_FOLDER'], output_filename, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)