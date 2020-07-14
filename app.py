from flask import Flask,render_template,request
import analyze_tweet

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/country",methods=['POST'])    
def country():
    return render_template('index.html')

@app.route("/state",methods=['POST'])    
def state():
    return render_template('index.html')

@app.route("/index.html")    
def index2():
    return render_template('index.html')   
    
@app.route("/dashboard.html")    
def dashboard():
    return render_template('dashboard.html')   
    
@app.route("/statistics.html")    
def statistics():
    return render_template('statistics.html')   
@app.route("/news_dashboard.html")
def news():
    return render_template('news_dashboard.html')
@app.route("/twitter_dashboard.html")
def twitter():
    return render_template('twitter_dashboard.html')
@app.route("/wiki_dashboard.html")
def wiki():
    return render_template('wiki_dashboard.html')
if __name__ =='__main__':
    analyze_tweet.analyze()
    app.run(debug=True)