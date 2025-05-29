from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML UI (included directly)
html = '''
<!DOCTYPE html>
<html>
<head>
  <title>WhatsApp Sender</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #f0f0f0; }
    .qr { margin: 20px 0; }
    input, button {
      padding: 10px;
      margin-top: 5px;
      width: 100%%;
      max-width: 400px;
      margin-bottom: 15px;
    }
    button { background: #28a745; color: white; border: none; cursor: pointer; }
    button:hover { background: #218838; }
  </style>
</head>
<body>
  <h2>💬 WhatsApp Automation Tool</h2>

  <button onclick="getQR()">🔐 Generate QR Code</button>
  <div class="qr" id="qrBox"></div>

  <hr>
  <form action="/send" method="POST" enctype="multipart/form-data">
    <label>📞 Target Number (with country code):</label><br>
    <input type="text" name="target" required><br>

    <label>📁 Upload Message File (.txt):</label><br>
    <input type="file" name="file" required><br>

    <label>⏱️ Delay (in seconds):</label><br>
    <input type="number" name="delay" required><br>

    <button type="submit">🚀 Send Messages</button>
  </form>

  <script>
    function getQR() {
      fetch('/get_qr')
        .then(res => res.json())
        .then(data => {
          if (data.qr) {
            document.getElementById('qrBox').innerHTML =
              `<img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${data.qr}" alt="QR Code">`;
          } else {
            alert("QR not generated. Maybe already connected?");
          }
        });
    }
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    return Response(html, mimetype='text/html')

@app.route('/get_qr')
def get_qr():
    try:
        res = requests.get('http://localhost:5001/qr')
        return res.json()
    except Exception as e:
        return {'error': str(e)}

@app.route('/send', methods=['POST'])
def send():
    try:
        target = request.form['target']
        delay = int(request.form['delay'])
        file = request.files['file']
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            messages = f.read()

        payload = {
            'target': target,
            'message': messages,
            'delay': delay
        }

        res = requests.post('http://localhost:5001/send', json=payload)
        return res.json()
    except Exception as e:
        return {'status': 'error', 'msg': str(e)}

if __name__ == '__main__':
    app.run(debug=True)
