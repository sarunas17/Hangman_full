import datetime
import logging
import secrets
from PIL import Image
import os
from flask import render_template, redirect, session, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required


from flask_mail import Message, Mail

from hangman import forms, db, app, bcrypt, mail
from datetime import datetime, timedelta
from hangman.models import User
from hangman.gamelogic import Hangman
from hangman.mongo_file import database, MongoCRUD

logging.basicConfig(level=logging.INFO, filename='hangman_log.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def registruotis():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.RegistracijosForma()
    if form.validate_on_submit():
        if form.tikrinti_pasta(form.email):
            return render_template("registruotis.html", title="Register", form=form)
        koduotas_slaptazodis = bcrypt.generate_password_hash(
            form.slaptazodis.data
        ).decode("utf-8")
        vartotojas = User(
            name=form.vardas.data,
            email=form.email.data,
            password=koduotas_slaptazodis,
        )
        db.session.add(vartotojas)
        db.session.commit()
        flash("Registration successful! You can login", "success")
        return redirect(url_for("index"))
    return render_template("registruotis.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def prisijungti():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.PrisijungimoForma()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.el_pastas.data).first()
        if user and bcrypt.check_password_hash(user.password, form.slaptazodis.data):
            login_user(user, remember=form.prisiminti.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash(
                "Login failed. Please check email and password", "danger"
            )
    return render_template("prisijungti.html", title="Prisijungti", form=form)


@app.route("/logout")
def atsijungti():
    logout_user()
    session.clear()
    return redirect(url_for("index"))


@app.route("/game", methods=["GET", "POST"])
def hangman_game():
    hangman_data = session.get("hangman")
    
   
    
    if request.method == "GET" or hangman_data is None:
        hangman = Hangman()
        hangman.start_game()  
        session["hangman"] = hangman.to_dict()
        logging.info("New game started")
        logging.info("Topic: %s", hangman.topic)
        logging.info("Word to guess: %s", hangman.word_to_guess)
        return render_template("game.html", hangman=hangman)

   
    elif request.method == "POST":
        guess = request.form.get("guess")
        hangman = Hangman.from_dict(hangman_data)       

        if not hangman.input_is_valid(guess):
            flash("You should guess only one letter or entire word!", "warning")

        if hangman.is_already_checked(guess):
            flash("You already guessed that letter!", "warning")
        else:
            if hangman.check_guess(guess):
                flash("Correct!", "success")
            else:
                flash("Incorrect!", "danger")

        
        if hangman.is_game_over():
            if current_user.is_authenticated and hangman.word_guessed_correctly():
                document = {"user_email": current_user.email, "mistakes_made": hangman.incorrect_guesses, "guesses_made": 10 - hangman.max_guesses, "guessed_letters": hangman.guessed_letters, "word_to_guess": hangman.word_to_guess, "status": "win", "timestamp": datetime.now()}
                database.insert_one_document(document)
            elif current_user.is_authenticated:
                document = {"user_email": current_user.email, "mistakes_made": hangman.incorrect_guesses, "guesses_made": 10 - hangman.max_guesses, "guessed_letters": hangman.guessed_letters, "word_to_guess": hangman.word_to_guess, "status": "lost", "timestamp": datetime.now()}
                database.insert_one_document(document)

   
        session["hangman"] = hangman.to_dict()

        return render_template("game.html", hangman=hangman, guess=guess)


@app.route("/gamestatistic")
@login_required
def game_statistic():
    user_email = current_user.email
    
    today = datetime.now().date()

    today_statistics = database.collection.find({"user_email": user_email,"timestamp": {"$gte": datetime.combine(today, datetime.min.time())}})

    previous_days_statistics = database.collection.find({"user_email": user_email,"timestamp": {"$lt": datetime.combine(today, datetime.min.time())}})

    today_statistics_list = list(today_statistics)
    previous_days_statistics_list = list(previous_days_statistics)

    return render_template("statistic.html", today_statistics=today_statistics_list, previous_days_statistics=previous_days_statistics_list, show_popup= True, datetime=datetime)

@app.route("/top10")
def top10():
    game_results = list(database.collection.find())

    wins_count = {}
    for result in game_results:
        if result["status"] == "win":
            player_email = result["user_email"]
            if player_email in wins_count:
                wins_count[player_email] += 1
            else:
                wins_count[player_email] = 1

    sorted_players = sorted(wins_count.items(), key=lambda x: x[1], reverse=True)

    top_10_players = sorted_players[:10]

    return render_template("top10.html", top_10_players=top_10_players)


@app.route("/account", methods=["GET", "POST"])
@login_required
def paskyra():
    form = forms.PaskyrosAtnaujinimoForma()
    if form.validate_on_submit():
        current_user.vardas = form.vardas.data
        current_user.el_pastas = form.el_pastas.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("paskyra"))
    elif request.method == "GET":
        form.vardas.data = current_user.name
        form.el_pastas.data = current_user.email
    return render_template("paskyra.html", title="Account", form=form)



@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = forms.UzklausosAtnaujinimoForma()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.el_pastas.data).first()
        send_reset_email(user)
        flash(
            "Jums išsiųstas el. laiškas su slaptažodžio atnaujinimo instrukcijomis.",
            "info",
        )
        return redirect(url_for("prisijungti"))
    return render_template("reset_request.html", title="Reset Password", form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Slaptažodžio atnaujinimo užklausa",
        sender="testflask11@gmail.com",
        recipients=[user.email],
    )
    msg.body = f"""Norėdami atnaujinti slaptažodį, paspauskite nuorodą:
    {url_for('reset_token', token=token, _external=True)}
    Jei jūs nedarėte šios užklausos, nieko nedarykite ir slaptažodis nebus pakeistas.
    """
    mail.send(msg)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Užklausa netinkama arba pasibaigusio galiojimo", "warning")
        return redirect(url_for("reset_request"))
    form = forms.SlaptazodzioAtnaujinimoForma()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.slaptazodis.data).decode(
            "utf-8"
        )
        user.slaptazodis = hashed_password
        db.session.commit()
        flash("Tavo slaptažodis buvo atnaujintas! Gali prisijungti", "success")
        return redirect(url_for("prisijungti"))
    return render_template("reset_token.html", title="Reset Password", form=form)


@app.errorhandler(404)
def klaida_404(klaida):
    return render_template("404.html"), 404


@app.errorhandler(403)
def klaida_403(klaida):
    return render_template("403.html"), 403


@app.errorhandler(500)
def klaida_500(klaida):
    return render_template("500.html"), 500
