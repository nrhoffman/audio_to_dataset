import configparser
from audiotodata import AudioToData
from flask import Flask, jsonify, request
from flask_cors import CORS
from psqlserve import PsqlServe

#Set up Flask:
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

#Read the config file
config = configparser.ConfigParser()
configPath = './backend/config/config.cfg'
config.read(configPath)

#Connect to Psql
connection = PsqlServe(config)

#Create Audio Convert Class
t2a = AudioToData(connection)

@app.route("/api/psql/droptables", defaults={'table': None}, methods=["GET"])
@app.route("/api/psql/droptable/<table>", methods=["GET"])
def droptables(table):
    data = connection.droptables(table)
    return jsonify(data)

@app.route("/api/psql/gettables", methods=["GET"])
def gettables():
    data = connection.gettables()
    return jsonify(data)

@app.route("/api/audio/storeaudio/<type>", methods=["GET"])
def storeaudio(type):
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    try:
        data = t2a.download_youtube_audio(url, type.lower())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/audio/audiotodata", methods=["GET"])
def audiotodata():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    data = t2a.wav_to_data(url)
    return jsonify(data)

@app.route("/api/audio/getoriginalwavs", methods=["GET"])
def getoriginalwavs():
    data = connection.getoriginalwavs()
    return jsonify(data)

if __name__ == "__main__":
   app.run(debug=True)