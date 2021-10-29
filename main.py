from flask import Flask, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import requests
import datetime

api_key = "api_key"
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
search = "/search/movie"
search_url = "https://api.themoviedb.org/3"+search
date = datetime.datetime.now()

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
all_rating = []
for num in numbers:
    for number in numbers:
        all_rating.append(float(f"{num}.{number}"))


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Float, nullable=False)
    review = db.Column(db.String(2500), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<Movies %r>' % self.ranking


class MovieAddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    year = StringField('Movie Year', validators=[DataRequired()])
    description = StringField('Movie Description', validators=[DataRequired()])
    rating = SelectField('Rating', validators=[DataRequired()], choices=all_rating)
    ranking = SelectField('Ranking', validators=[DataRequired()], choices=all_rating)
    review = StringField('Movie Review', validators=[DataRequired()])
    img_url = StringField('Movie Img-URL', validators=[DataRequired()])
    add_button = SubmitField('Add Movie')


class MovieEditForm(FlaskForm):
    review = StringField('Movie review')
    rating = SelectField('Rating', choices=all_rating)
    edit_button = SubmitField('Edit Movie')


class MovieQuery(FlaskForm):
    query = StringField('Movie Title', validators=[DataRequired()])
    query_button = SubmitField('Look Movie')


db.create_all()


@app.route("/")
def home():
    movies = db.session.query(Movies).all()
    print(date.year)
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=movies, year=date.year)


@app.route("/add", methods=['POST', 'GET'])
def add():
    form = MovieAddForm()
    if form.validate_on_submit():
        new_movie = Movies(
            title=form.title.data,
            year=form.year.data,
            description=form.description.data,
            rating=form.rating.data,
            ranking=form.ranking.data,
            review=form.review.data,
            img_url=form.img_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect("/")
    return render_template("add.html", form=form, year=date.year)


@app.route("/add_query/<id>")
def add_query(id):
    try:
        res = requests.get(f"https://api.themoviedb.org/3/movie/{id}/external_ids?api_key={api_key}")
        res = res.json()
        movie_id = res["imdb_id"]
        movie = requests.get(f"https://api.themoviedb.org/3/find/{movie_id}?api_key={api_key}&external_source=imdb_id")
        movie = movie.json()["movie_results"][0]

        new_movie = Movies(
            title=movie["original_title"],
            year=movie["release_date"],
            description=movie["overview"],
            rating=movie["vote_average"],
            ranking=movie["popularity"],
            review="Edit and add your own review",
            img_url=f"https://image.tmdb.org/t/p/w500"+movie["poster_path"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        print(e)


@app.route("/query", methods=['POST', 'GET'])
def query():
    form = MovieQuery()
    if form.validate_on_submit():
        try:
            res = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={form.query.data}")
            res.raise_for_status()
            res = res.json()
            return render_template("query.html", movies=res["results"], year=date.year)

        except Exception as e:
            print(e)

    return render_template("add.html", form=form, year=date.year)


@app.route('/delete/<id>')
def delete(id):
    movie = Movies.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect("/")


@app.route('/edit/<id>', methods=['POST', 'GET'])
def edit(id):
    form = MovieEditForm()
    movie = Movies.query.get(id)
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()

        return redirect("/")
    return render_template("edit.html", form=form, movie=movie)


@app.route("/footer")
def footer():
    return render_template("base.html", year=date.year)


if __name__ == '__main__':
    app.run(debug=True)
