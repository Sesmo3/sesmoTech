from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import glob

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    fmt = request.form["format"]

    # Set file extension
    ext = "mp3" if fmt == "mp3" else "mp4"

    # Setup yt-dlp options
    ydl_opts = {
        "format": "bestaudio/best" if fmt == "mp3" else "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True,
    }

    # Add postprocessing for audio
    if fmt == "mp3":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]

    # Ensure download folder exists
    os.makedirs("downloads", exist_ok=True)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            downloaded_filename = ydl.prepare_filename(info)

            # If mp3, adjust extension
            if fmt == "mp3":
                downloaded_filename = downloaded_filename.rsplit(".", 1)[0] + ".mp3"

        response = send_file(downloaded_filename, as_attachment=True)

        @response.call_on_close
        def cleanup():
            if os.path.exists(downloaded_filename):
                os.remove(downloaded_filename)

        return response

    except Exception as e:
        return f"<h2>Download Failed</h2><p>{str(e)}</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
