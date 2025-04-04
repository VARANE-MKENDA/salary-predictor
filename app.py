from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pickle
import os

db = SQLAlchemy()
app = Flask(__name__, template_folder=os.path.join(os.getcwd(),"templates"))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

model= pickle.load(open('model.pkl', "rb"))

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    years_experience = db.Column(db.Float, nullable=False)
    predicted_salary = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            years_experience = float(request.form['years_experience'])
            predicted_salary = model.predict([[years_experience]])[0]
            new_prediction = Prediction(years_experience=years_experience, predicted_salary=predicted_salary)
            db.session.add(new_prediction)
            db.session.commit()
        except:
            pass
    predictions = Prediction.query.all()
    return render_template('index.html', predictions=predictions)

@app.route('/delete/<int:id>')
def delete(id):
    prediction = Prediction.query.get(id)
    if prediction:
        db.session.delete(prediction)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    prediction = Prediction.query.get(id)
    if request.method == 'POST':
        try:
            new_experience = float(request.form['years_experience'])
            new_salary = model.predict([[new_experience]])[0]
            prediction.years_experience = new_experience
            prediction.predicted_salary = new_salary
            db.session.commit()
        except:
            pass
        return redirect(url_for('index'))
    return render_template('update.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)

