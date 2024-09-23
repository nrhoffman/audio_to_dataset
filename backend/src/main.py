import configparser
from flask import Flask, jsonify, request
from psqlserve import PsqlServe
from audiotodata import AudioToData

#Set up Flask:
app = Flask(__name__)

#Read the config file
config = configparser.ConfigParser()
configPath = './backend/config/config.cfg'
config.read(configPath)

#Connect to Psql
connection = PsqlServe(config)

#Create Audio Convert Class
t2a = AudioToData(connection)

@app.route("/api/psql/createtables", methods=["GET"])
def createtables():
    data = connection.createtables()
    return jsonify(data)

@app.route("/api/psql/droptables", defaults={'table': None}, methods=["GET"])
@app.route("/api/psql/droptable/<table>", methods=["GET"])
def droptables(table):
    data = connection.droptables(table)
    return jsonify(data)

@app.route("/api/psql/gettables", methods=["GET"])
def gettables():
    data = connection.gettables()
    return jsonify(data)

@app.route("/api/audio/storeaudio", methods=["GET"])
def storeaudio():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    data = t2a.download_youtube_audio(url)
    return jsonify(data)

@app.route("/api/audio/audiotodata", methods=["GET"])
def audiotodata():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    data = t2a.wav_to_data(url)
    return jsonify(data)

@app.route("/api/audio/getdata/<table>/<type>", methods=["GET"])
def getdata(table, type):
    data = connection.getdata(table, type)
    return jsonify(data)

if __name__ == "__main__": 
   app.run(debug=True)