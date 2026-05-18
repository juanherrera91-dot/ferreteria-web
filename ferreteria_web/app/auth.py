from flask import Blueprint, render_template, request, redirect, session
from .models import Usuario
from .extensions import db, bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']

        usuario = Usuario.query.filter_by(username=user).first()

        if usuario and bcrypt.check_password_hash(usuario.password, passw):
            session['user'] = usuario.username
            return redirect('/dashboard')

        return "❌ Usuario o contraseña incorrectos"

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')