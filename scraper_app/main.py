from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
from collections import Counter

import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SECRET_KEY'] = 'secret key'
db = SQLAlchemy(app)
db.create_all()

api = Api(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50000))
    url = db.Column(db.String(50000))

def scraper(html_url):
    response = requests.get(html_url)
    soup = BeautifulSoup(response.content, 'lxml')
    page_content = soup.find('div', attrs={'class': 'mw-parser-output'}).text
    return page_content
    
def parser(page_content):
    words = page_content.split()
    dict = Counter(words)
    return dict

def to_json(counter):
    counter_json = json.dumps(counter)
    return counter_json

def json_to_database(counter_json, url_scrap):
    if db.session.query(Post.id).filter_by(url=url_scrap).first() is None:
        new = Post(
            content = counter_json,
            url = url_scrap
        )
        db.session.add(new)
        db.session.commit()
        return jsonify({"message": "L'enregistrement dans la base de données est un succès"})
    else:
        return jsonify({"message": "L'enregistrement existe déjà dans la base données"})

def get_url_from_db():
    url_query = db.session.query(Post.url)
    url_list = []
    for url in url_query:
        url_list.append(url[0])
    return url_list

def delete_url(html_url):
    db.session.query(Post).filter(Post.url==html_url).delete()
    db.session.commit()  

class Home(Resource):
    def get(self):
        url_list = get_url_from_db()
        return jsonify(url_list)

class Scrap(Resource):
    def get(self, url_end):
        string = 'https://wikipedia.org/wiki/'
        full_url = string + url_end
        scrap = scraper(full_url)
        counter = parser(scrap)
        counter_json = to_json(counter)
        message = json_to_database(counter_json, full_url)
        return message
    
    def delete(self, url_end):
        string = 'https://wikipedia.org/wiki/'
        full_url = string + url_end
        delete_url(full_url)
        return jsonify({"message": "URL supprimer de la base de données"})

class Delete_db(Resource):
    def delete(self):
        db.session.query(Post).delete()
        db.session.commit()
        return jsonify({"message": "La base de données a été vidé"})

api.add_resource(Home, '/')
api.add_resource(Scrap, '/scrap/<string:url_end>')
api.add_resource(Delete_db, '/delete_db')

if __name__ == "__main__":
    app.run(debug=True)
