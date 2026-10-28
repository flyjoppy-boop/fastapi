from flask import Flask, request
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 최대 10MB

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or not file.filename:
            return "파일을 선택하세요.", 400

        filename = secure_filename(file.filename)

        if not filename:
            return "사용할 수 없는 파일명입니다.", 400

        destination = UPLOAD_DIR / filename

        if destination.exists():
            return "같은 이름의 파일이 이미 존재합니다.", 409

        file.save(destination)
        return "업로드 완료!"

    return """
    <h2>파일 업로드 서버</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">업로드</button>
    </form>
    """

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
