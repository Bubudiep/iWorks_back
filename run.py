# run.py
from app import create_app
import platform
app = create_app()

if __name__ == '__main__':
    if platform.system() == "Windows":
        app.run(ssl_context=('cert.pem', 'key.pem'),debug=True,host='0.0.0.0', port=5000)
    else:
        app.run(ssl_context='adhoc',debug=True,host='0.0.0.0', port=5000)
