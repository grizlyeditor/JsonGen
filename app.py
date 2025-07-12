from flask import Flask, render_template, request, send_file
import zipfile, os, json, shutil
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'zipfile' not in request.files:
        return "No file part", 400

    file = request.files['zipfile']
    if file.filename == '':
        return "No selected file", 400

    os.makedirs("temp", exist_ok=True)
    zip_path = os.path.join("temp", "uploaded.zip")
    file.save(zip_path)

    extract_path = os.path.join("temp", "unzipped")
    os.makedirs(extract_path, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    accounts = []
    for root, dirs, files in os.walk(extract_path):
        for name in files:
            try:
                with open(os.path.join(root, name), 'r') as f:
                    lines = f.readlines()
                    uid = ""
                    password = ""
                    for line in lines:
                        if "uid=" in line:
                            uid = line.strip().split("=")[1]
                        elif "password=" in line:
                            password = line.strip().split("=")[1]
                    if uid and password:
                        accounts.append({"uid": uid, "password": password})
            except Exception as e:
                print("Error in file:", name, "->", e)

    json_path = os.path.join("temp", f"accounts_{datetime.now().timestamp()}.json")
    with open(json_path, 'w') as jf:
        json.dump(accounts, jf, indent=4)

    shutil.rmtree("temp")  # clean after processing
    return send_file(json_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
