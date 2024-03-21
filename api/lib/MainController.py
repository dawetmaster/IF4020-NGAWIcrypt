from flask import Flask, request, flash, jsonify,send_file
from werkzeug.utils import secure_filename
from Cipher import Cipher
import time
import os
import uuid
import base64
import time


def register_controllers(app: Flask):
    @app.route("/")
    def main():
        return "Connected"

    @app.route("/encrypt", methods=["POST"])
    def encrypt():
        # baca plaintext
        plaintext = ""
        original_filename = ""
        if "file" in request.files:
            file = request.files["file"]
            if not file:
                flash("No file received")
                return "File not found", 400
            # baca file
            plaintext = file.stream.read()
            original_filename = file.filename
        else:
            # plaintext murni
            plaintext = str.encode(request.form["plaintext"])
        # baca mode
        mode = request.form["mode"]
        # baca key
        key = str.encode(request.form["key"])
        # encrypt
        cipher = Cipher()
        start_time = time.time()
        ciphertext = cipher.encrypt(plaintext, key, mode)
        execution_time = time.time() - start_time
        # save temp file
        filename = ""
        if original_filename != "":
            names = original_filename.rsplit(".", 1)
            filename = f"{secure_filename(names[0])}-{str(int(time.time()))}-encrypted.{names[1]}"
        else:
            filename = f"{str(uuid.uuid4())}-encrypted.txt"
        # simpan dulu
        ciphertext_path = os.path.join(app.config["UPLOAD_PATH"], filename)
        with open(ciphertext_path, "wb") as f:
            f.write(ciphertext)
        # bikin json
        return jsonify(
            {"ciphertext": base64.b64encode(ciphertext), "elapsed_time": execution_time,'download_filename':filename}
        )

    @app.route("/decrypt", methods=["POST"])
    def decrypt():
      # baca ciphertext
      ciphertext = ""
      original_filename = ""
      if "file" in request.files:
          file = request.files["file"]
          if not file:
              flash("No file received")
              return "File not found", 400
           # baca file
          ciphertext = file.stream.read()
          original_filename = file.filename
      else:
          # plaintext murni
          ciphertext = str.encode(request.form["ciphertext"])
      # baca mode
      mode = request.form["mode"]
      # baca key
      key = str.encode(request.form["key"])
      # decrypt
      cipher = Cipher()
      start_time = time.time()
      plaintext = cipher.decrypt(ciphertext, key, mode)
      execution_time = time.time() - start_time
      # save temp file
      filename = ""
      if original_filename != "":
          names = original_filename.rsplit(".", 1)
          filename = f"{secure_filename(names[0])}-{str(int(time.time()))}-decrypted.{names[1]}"
      else:
          filename = f"{str(uuid.uuid4())}-decrypted.txt"
      # simpan dulu
      plaintext_path = os.path.join(app.config["UPLOAD_PATH"], filename)
      with open(plaintext_path, "wb") as f:
          f.write(plaintext)
      # bikin json
      return jsonify(
          {"plaintext": base64.b64encode(plaintext), "elapsed_time": execution_time,'download_filename':filename}
      )

    @app.route("/download/<filename>", methods=["GET"])
    def download(filename):
      # read file
      return send_file(os.path.join(app.config["UPLOAD_PATH"], filename),as_attachment=True,download_name=filename)
          