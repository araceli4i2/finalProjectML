import sys
import os

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from dashboard.app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5055))
    print(f"Iniciando servidor en http://127.0.0.1:{port}", flush=True)
    app.run(host='127.0.0.1', port=port, debug=False)
