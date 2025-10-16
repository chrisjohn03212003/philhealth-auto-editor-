# app.py
import os
from flask import Flask, request, send_from_directory, render_template, jsonify
from werkzeug.utils import secure_filename
from logic.utils import load_docx, save_docx, find_detailed_table, normalize_and_map_items
from logic.regular import process_regular
from logic.nondrugs import process_nondrugs
from logic.senior import process_senior

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
TEMPLATE_FOLDER = 'templates'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['TEMPLATE_FOLDER'] = TEMPLATE_FOLDER

TEMPLATE_MAP = {
    'regular': 'reference_regular.docx',
    'nondrugs': 'reference_nondrugs.docx',
    'senior': 'reference_senior.docx',
}

PROCESSORS = {
    'regular': process_regular,
    'nondrugs': process_nondrugs,
    'senior': process_senior,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    category = request.form.get('category')
    if category not in TEMPLATE_MAP:
        return jsonify({'error': 'Invalid category'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    # Load uploaded and template docs
    template_path = os.path.join(app.config['TEMPLATE_FOLDER'], TEMPLATE_MAP[category])
    doc_uploaded = load_docx(upload_path)
    doc_template = load_docx(template_path)

    # Run category-specific processing
    processor = PROCESSORS[category]
    out_doc, output_name = processor(doc_uploaded, doc_template, filename)

    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_name)
    save_docx(out_doc, output_path)

    return jsonify({'download': f'/download/{output_name}'})

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
