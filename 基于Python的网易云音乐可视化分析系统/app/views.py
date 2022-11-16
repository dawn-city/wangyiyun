from app import app
from app.echarts import *
from flask import request,render_template,g



@app.route("/")
def index():
    return render_template("summary.html")

@app.route("/songs")
def songs():
    return render_template("songs.html")


@app.route("/artists")
def artists():
    return render_template("artists.html")

@app.route("/emotion")
def emotion():
    return render_template("emotion.html")

@app.route("/api")
def api():
    type=request.args.get('type')
    tag=request.args.get('tag')
    if tag:
        return render_emotion(type,tag)
    else:
        return render_echarts(type)



if __name__ == "__main__":
    app.run(debug=True)