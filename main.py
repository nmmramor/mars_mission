from flask import Flask
import scrape_mars
import pymongo

app = Flask(__name__)

@app.route("/scrape")
def scrape_data():
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn) 
    db = client.mars_db
    
    mars_collection = db.mars_mission

    scraped = scrape_mars.scrape()
    mars_collection.insert_one(scraped)
    
    return scraped