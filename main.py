from flask import Flask, render_template
import scrape_mars
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient('mongodb://localhost:27017') 
mars_collection = client.mars_db.mars_mission

@app.route("/scrape")
def scrape_data():
    scraped = scrape_mars.scrape()
    mars_collection.insert_one(scraped)
    
    return scraped

@app.route("/")
def index():
    mars = mars_collection.find_one()
    return render_template("index.html", mars=mars)


if __name__ == "__main__":
    app.run()