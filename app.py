from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy.orm import Mapped, mapped_column
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzeria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

class Pizza(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    ingredients: Mapped[str] = mapped_column(db.String(200), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

class Review(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    comment: Mapped[str] = mapped_column(db.String(200), nullable=False)
    rating: Mapped[str] = mapped_column(db.String(10), nullable=False)

class Survey(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    favorite_pizza: Mapped[str] = mapped_column(db.String(100), nullable=False)

class ReviewForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    rating = RadioField('Rating', choices=[('good', 'Good'), ('bad', 'Bad')], validators=[DataRequired()])
    submit = SubmitField('Submit')

def init_db():
    db.create_all()
    if not Pizza.query.first():
        pizzas = [
            {'name': 'Margherita', 'ingredients': 'Tomato, Mozzarella, Basil', 'price': 8.99},
            {'name': 'Pepperoni', 'ingredients': 'Tomato, Mozzarella, Pepperoni', 'price': 9.99},
            {'name': 'Hawaiian', 'ingredients': 'Tomato, Mozzarella, Ham, Pineapple', 'price': 10.99},
        ]
        for pizza in pizzas:
            new_pizza = Pizza(name=pizza['name'], ingredients=pizza['ingredients'], price=pizza['price'])
            db.session.add(new_pizza)
        db.session.commit()
        print("Initial pizzas added to the database.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        favorite_pizza = request.form['favorite_pizza']
        survey = Survey(favorite_pizza=favorite_pizza)
        db.session.add(survey)
        db.session.commit()
        return redirect(url_for('survey_results'))
    return render_template('survey.html')

@app.route('/survey/results')
def survey_results():
    survey_results = Survey.query.all()
    return render_template('survey_results.html', survey_results=survey_results)

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    form = ReviewForm()
    if form.validate_on_submit():
        name = form.name.data
        comment = form.comment.data
        rating = form.rating.data
        review = Review(name=name, comment=comment, rating=rating)
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('reviews'))
    reviews = Review.query.all()
    return render_template('reviews.html', form=form, reviews=reviews)

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('pizzeria.db'):
            init_db()
    app.run(debug=True)