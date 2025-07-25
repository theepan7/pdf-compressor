from flask import Flask, request, send_file
import os
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route('/compress', methods=['POST'])
def compress_pdf():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return 'No file uploaded', 400

    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
    output_path = os.path.join(COMPRESSED_FOLDER, f"{uuid.uuid4()}_compressed.pdf")
    uploaded_file.save(input_path)

    gs_cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(gs_cmd, check=True)
        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError:
        return 'Compression failed', 500
    finally:
        os.remove(input_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
