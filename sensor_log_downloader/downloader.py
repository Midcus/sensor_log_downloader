import os
import logging
from datetime import datetime
from flask import Flask, send_file, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, template_folder="/app/templates")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

SOURCE_DB = "/config/home-assistant_v2.db"
LOG_FILE = "/tmp/addon.log"

logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def db_info():
    """Return (exists, size_bytes, mtime_iso)."""
    if not os.path.exists(SOURCE_DB):
        return False, None, None

    try:
        st = os.stat(SOURCE_DB)
        size = st.st_size
        mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return True, size, mtime
    except Exception as e:
        logger.error(f"Failed to stat db: {e}")
        return True, None, None


def tail_logs(n=10):
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()[-n:]
    except Exception:
        return []


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})


# Ingress root (support subpaths)
@app.route("/", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def index(path):
    exists, size, mtime = db_info()
    logs = tail_logs(12)

    return render_template(
        "index.html",
        db_ok=exists,
        db_size=size,
        db_mtime=mtime,
        logs=logs,
    )


@app.route("/download", defaults={"path": ""}, methods=["GET"])
@app.route("/<path:path>/download", methods=["GET"])
def download_db(path=None):
    if not os.path.exists(SOURCE_DB):
        logger.error("Download failed: database not found")
        return jsonify({"status": "error", "message": "Database file not found"}), 404

    try:
        logger.info(f"Download requested: {SOURCE_DB}")
        # Stream directly from /config (no copy, no zip)
        return send_file(
            SOURCE_DB,
            as_attachment=True,
            download_name="home-assistant_v2.db",
            mimetype="application/octet-stream",
            conditional=True,
        )
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    ok, _, _ = db_info()
    if ok:
        logger.info(f"Database file found at: {SOURCE_DB}")
    else:
        logger.error(f"Database file not found at: {SOURCE_DB}")

    logger.info("Starting Sensor Historie Downloader")
    app.run(host="0.0.0.0", port=5000, debug=False)
