from flask import flash
from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, FloatField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from flask_wtf.file import FileField, FileAllowed
from hangman import User, current_user


class RegistracijosForma(FlaskForm):
    vardas = StringField('Name', [DataRequired()])
    email = StringField('Email', [DataRequired()])
    slaptazodis = PasswordField('Password', [DataRequired()])
    patvirtintas_slaptazodis = PasswordField("Repeat your password", [EqualTo('slaptazodis', "Passwords should be the same")])
    submit = SubmitField('Sing up')

    def tikrinti_pasta(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            flash('This email is occupied! Please choose another one.', 'danger')
            return True
        return False

class PrisijungimoForma(FlaskForm):
    el_pastas = StringField('Email', [DataRequired()])
    slaptazodis = PasswordField('Password', [DataRequired()])
    prisiminti = BooleanField("Remember me")
    submit = SubmitField('LOG IN')

class IrasasForm(FlaskForm):
    pajamos = BooleanField('Pajamos')
    suma = FloatField('Suma', [DataRequired()])
    submit = SubmitField('Įvesti')

class PaskyrosAtnaujinimoForma(FlaskForm):
    vardas = StringField('Name', [DataRequired()])
    el_pastas = StringField('Email', [DataRequired()])
    # nuotrauka = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # def tikrinti_varda(self, vardas):
    #     if vardas.data != current_user.vardas:
    #         vartotojas = User.query.filter_by(vardas=vardas.data).first()
    #         if vartotojas:
    #             raise ValidationError('Šis vardas panaudotas. Pasirinkite kitą.')

    def tikrinti_pasta(self, el_pastas):
        if el_pastas.data != current_user.el_pastas:
            vartotojas = User.query.filter_by(el_pastas=el_pastas.data).first()
            if vartotojas:
                raise ValidationError('Šis el. pašto adresas panaudotas. Pasirinkite kitą.')
            
class UzklausosAtnaujinimoForma(FlaskForm):
    el_pastas = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, el_pastas):
        user = User.query.filter_by(el_pastas=el_pastas.data).first()
        if user is None:
            raise ValidationError('Nėra paskyros, registruotos šiuo el. pašto adresu. Registruokitės.')
        
class SlaptazodzioAtnaujinimoForma(FlaskForm):
    slaptazodis = PasswordField('Slaptažodis', validators=[DataRequired()])
    patvirtintas_slaptazodis = PasswordField('Pakartokite slaptažodį', validators=[DataRequired(), EqualTo('slaptazodis')])
    submit = SubmitField('Atnaujinti Slaptažodį')

