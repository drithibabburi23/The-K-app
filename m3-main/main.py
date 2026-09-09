"""KarigarConnect image AI API."""

from __future__ import annotations

import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_from_directory
from werkzeug.utils import secure_filename

from image_processor import process_image

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KarigarConnect Image AI</title>
<style>
body{font-family:Georgia,serif;background:#f5efe5;color:#2d2a26;margin:0;padding:48px 20px}main{max-width:680px;margin:auto;background:#fffdf9;padding:42px;border:1px solid #dfd2bf}h1{font-size:42px;margin:0 0 8px;color:#8a3d2f}p{font:16px Arial,sans-serif;line-height:1.5}form{margin-top:30px;padding:28px;background:#f0e4d2;border:1px dashed #b68b67}input,button{font:16px Arial,sans-serif}button{background:#8a3d2f;color:white;border:0;padding:13px 20px;cursor:pointer;margin-top:18px}button:hover{background:#672d24}.result img{max-width:100%;margin-top:18px;border:1px solid #dfd2bf}.result a{font:15px Arial,sans-serif;color:#8a3d2f}
</style></head><body><main><h1>KarigarConnect</h1><p>From craft to customer. Turn a product photo into a clean marketplace listing image.</p>
<form action="/process" method="post" enctype="multipart/form-data"><input type="file" name="image" accept="image/*" required><br><button type="submit">Clean my product photo</button></form>{% if result %}<section class="result"><h2>Ready for your marketplace</h2><img src="{{ result }}" alt="Processed artisan product"><p><a href="{{ result }}" download>Download image</a></p></section>{% endif %}{% if error %}<p role="alert">{{ error }}</p>{% endif %}</main></body></html>"""


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/process")
def process():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename:
        return render_template_string(PAGE, error="Please choose an image first."), 400
    if not allowed_file(uploaded.filename):
        return render_template_string(PAGE, error="Use a JPG, PNG, or WEBP image."), 400

    token = secrets.token_hex(6)
    original_name = secure_filename(uploaded.filename)
    input_path = UPLOAD_DIR / f"{token}_{original_name}"
    output_path = OUTPUT_DIR / f"karigar_{token}.jpg"
    uploaded.save(input_path)

    try:
        process_image(input_path, output_path)
    except (OSError, ValueError) as exc:
        return render_template_string(PAGE, error=f"We could not process that image: {exc}"), 422

    return render_template_string(PAGE, result=f"/outputs/{output_path.name}")


@app.get("/outputs/<path:filename>")
def output_file(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


@app.post("/api/process")
def api_process():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename or not allowed_file(uploaded.filename):
        return jsonify({"error": "Upload a JPG, PNG, or WEBP file as 'image'."}), 400

    token = secrets.token_hex(6)
    input_path = UPLOAD_DIR / f"{token}_{secure_filename(uploaded.filename)}"
    output_path = OUTPUT_DIR / f"karigar_{token}.jpg"
    uploaded.save(input_path)
    process_image(input_path, output_path)
    return jsonify({"image_url": f"/outputs/{output_path.name}", "filename": output_path.name})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
