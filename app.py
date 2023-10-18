from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from decouple import config

MONGO_URI = config('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client.dbsparta


# Flask
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

# POST

@app.route("/food", methods=["POST"])
def food_post():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']
    category_receive = request.form['category_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    title = soup.select_one(
        'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > header > div.restaurant_title_wrap > span > h1').text
    ogimage = soup.select_one('meta[property="og:image"]')['content']
    location = soup.select_one(
        'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr.only-desktop > td > span.Restaurant__InfoAddress--Text').text
    information = soup.select(
        'body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr')

    doc = {
        'title': title,
        'image': ogimage,
        'location': location,
        'comment': comment_receive,
        'star': star_receive,
        'category': category_receive,
        'information': [],
    }

    for infs in information:
        th = infs.select_one('th').text
        td = infs.select_one('td').text.strip("\n")
        doc['information'].append({
            th: td,
        })

    # print(doc)
    db.food.insert_one(doc)
    return jsonify({'msg': '저장 완료!'})

# GET

@app.route("/food", methods=["GET"])
def food_get():
    all_food = list(db.food.find({}, {'_id': False}))
    return jsonify({'result': all_food})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
