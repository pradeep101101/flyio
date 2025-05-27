from flask import Flask, render_template, request, send_file, jsonify
import os
from moviepy.editor import VideoFileClip
import logging
import tempfile # For more robust temporary file/directory handling

app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads' # We'll use a temporary directory per request
# os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Not strictly needed with tempfile

logging.basicConfig(level=logging.INFO) # INFO is often better for production than DEBUG
app.logger.setLevel(logging.INFO)


@app.route('/')
def index_route():
    app.logger.debug("Serving index.html for GET /") # DEBUG for less frequent logs
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    app.logger.info("Received POST request to /convert")
    if 'video' not in request.files:
        app.logger.error("No 'video' file part in request to /convert")
        return jsonify(error='No file part in the request'), 400

    file = request.files['video']
    if file.filename == '':
        app.logger.error("No selected file in request to /convert")
        return jsonify(error='No file selected'), 400

    if file:
        original_filename = file.filename
        # Create a temporary directory for this request's files
        with tempfile.TemporaryDirectory() as temp_dir:
            app.logger.info(f"Created temporary directory: {temp_dir}")
            filepath = os.path.join(temp_dir, original_filename)
            
            app.logger.info(f"Attempting to save file to: {filepath}")
            try:
                file.save(filepath)
                app.logger.info(f"File saved successfully: {filepath}")
            except Exception as e:
                app.logger.error(f"Error saving file '{filepath}': {e}")
                return jsonify(error=f"Could not save file: {e}"), 500

            audio_filename_base = original_filename.rsplit('.', 1)[0]
            audio_filename = audio_filename_base + '.mp3'
            audio_path = os.path.join(temp_dir, audio_filename)
            app.logger.info(f"Attempting to convert video '{filepath}' to audio: {audio_path}")

            try:
                video_clip = VideoFileClip(filepath)
                video_clip.audio.write_audiofile(audio_path, logger=None) # Can set logger='bar' or None
                video_clip.close()
                app.logger.info(f"Audio conversion successful: {audio_path}")

                return send_file(audio_path,
                                 as_attachment=True,
                                 download_name=audio_filename,
                                 mimetype='audio/mpeg')
            except Exception as e:
                app.logger.error(f"Error during video conversion for '{filepath}': {e}")
                # Try to close clip even on error if it was opened
                if 'video_clip' in locals() and video_clip:
                    video_clip.close()
                return jsonify(error=f"Error during video conversion: {str(e)}"), 500
            # The 'temp_dir' and its contents (filepath, audio_path) 
            # will be automatically cleaned up when exiting the 'with' block.

    app.logger.error("File object was not valid in /convert")
    return jsonify(error='Invalid file object.'), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080)) # For compatibility if run directly
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False for production
                                                 # Gunicorn will run this, so this block is more for local testing