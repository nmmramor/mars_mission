from flask import Flask, render_template
import scrape_mars
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient('mongodb://localhost:27017') 
mars_collection = client.mars_db.mars_mission

@app.route("/scrape")
def scrape_data():
    scraped = populate_mars_data()
    
    return render_template("index.html", mars=scraped)


def populate_mars_data():
    scraped = scrape_mars.scrape()
    
    mars_collection.update({}, scraped, upsert=True)
    return scraped


@app.route("/")
def index():
    mars = mars_collection.find_one()
    
    # if there's no data in the database, initialize it.
    if mars is None:
        mars = populate_mars_data()
    
    return render_template("index.html", mars=mars)


if __name__ == "__main__":
    app.run()