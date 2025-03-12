from flask import Flask, render_template
import os

app = Flask(__name__)

# Serve the AR index.html from the static directory
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Path to the certificate and private key
    cert_path = os.path.join('certs', 'cert.pem')
    key_path = os.path.join('certs', 'key.pem')
    
    # Run the Flask server with HTTPS enabled
    app.run(host='0.0.0.0', port=8000, ssl_context=(cert_path, key_path))
