from flask import Flask, request, send_file, render_template
import os
import uuid
import subprocess
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    uploaded_file = request.files['file']
    if uploaded_file.filename.endswith('.pdf'):
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.pdf")
        output_path = os.path.join(PROCESSED_FOLDER, f"{file_id}_compressed.pdf")
        uploaded_file.save(input_path)

        try:
            subprocess.run([
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/ebook",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-sOutputFile={output_path}",
                input_path
            ], check=True)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Compression failed: {e}", 500
    return "Invalid file", 400

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('files')
    merger = PdfMerger()
    file_id = str(uuid.uuid4())
    output_path = os.path.join(PROCESSED_FOLDER, f"{file_id}_merged.pdf")

    try:
        for file in files:
            if file.filename.endswith('.pdf'):
                merger.append(PdfReader(file.stream))
        with open(output_path, 'wb') as f_out:
            merger.write(f_out)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Merging failed: {e}", 500

@app.route('/split', methods=['POST'])
def split():
    file = request.files['file']
    start = int(request.form['start'])
    end = int(request.form['end'])

    if file and file.filename.endswith('.pdf'):
        file_id = str(uuid.uuid4())
        output_path = os.path.join(PROCESSED_FOLDER, f"{file_id}_split.pdf")
        reader = PdfReader(file.stream)
        writer = PdfWriter()

        try:
            for i in range(start - 1, end):
                writer.add_page(reader.pages[i])
            with open(output_path, 'wb') as f_out:
                writer.write(f_out)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Splitting failed: {e}", 500
    return "Invalid file", 400

if __name__ == "__main__":
    app.run(debug=True)
