from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def getMoviesList():
    raw = requests.get("https://amctheatres.com/movies").text
    soup = BeautifulSoup(raw, 'lxml')
    moviesList = []

    for moviesInfo in soup.find_all('div', class_='PosterContent'):
        movieTitle = moviesInfo.h3.text
        moviesList.append(movieTitle)
 
    return moviesList

def isPlaying(movieName):
    for x in getMoviesList():
        if x == movieName:
            return True
    return False

def getPosterSource(movieName):
    raw = requests.get("https://amctheatres.com/movies").text
    soup = BeautifulSoup(raw, 'lxml')
    
    for poster in soup.find_all('img'):
        if poster.attrs.get('alt') == "movie poster for " + movieName:
            return (poster.attrs.get('src'))

def getCriticReviews(movieName):
    #In case the movie name is more than one word, need to replace spaces with underscores
    split = movieName.split()
    newName = ""
    for x in split:
        newName += "_" + x
    newName = newName[1:len(newName)]
    
    url = "https://rottentomatoes.com/m/" + newName.lower() + "/reviews"
    print(url)
    criticsReviews = []

    raw = requests.get(url).text
    soup = BeautifulSoup(raw, 'lxml')
    for reviewArea in soup.find_all('p', class_='review-text'):
        review = reviewArea.text 
        criticsReviews.append(review)
    
    if len(criticsReviews) == 0:
        print("No critic reviews for " + movieName + ". ")
    return criticsReviews

def getUserReviews(movieName):
     #In case the movie name is more than one word, need to replace spaces with underscores
    split = movieName.split()
    newName = ""
    for x in split:
        newName += "_" + x
    newName = newName[1:len(newName)]

    url = "https://rottentomatoes.com/m/" + newName.lower() + "/reviews?type=user"
    usersReviews = []

    raw = requests.get(url).text
    soup = BeautifulSoup(raw, 'lxml')
    for reviewArea in soup.find_all('p', class_="audience-reviews__review js-review-text"):
        userReview = reviewArea.text
        usersReviews.append(userReview.lstrip().rstrip())
    
    if len(usersReviews) == 0:
        print("No audience reviews for " + movieName + ". ")
    return usersReviews

def getMovieInfo(movieName):
    info = {}
    info['poster'] = getPosterSource(movieName)
    info['playing'] = isPlaying(movieName)
    return info


#routes
@app.route('/amc/<movieName>', methods =['GET'])
def get_movie_info(movieName):
    info = {}
    info['poster'] = getPosterSource(movieName)
    info['playing'] = isPlaying(movieName)
    print(info["poster"])
    return jsonify(info)

@app.route('/rottenTomatoes/user/<movieName>', methods=['GET'])
def get_user_reviews(movieName):
    reviews = {}
    reviews['reviews'] = getUserReviews(movieName)
    return jsonify(reviews)

@app.route('/rottenTomatoes/critic/<movieName>', methods=['GET'])
def get_critic_reviews(movieName):
    reviews = {}
    reviews['reviews'] = getCriticReviews(movieName)
    print(reviews['reviews'])
    return jsonify(reviews)

if __name__ == ("__main__"):
    app.run()