from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from forms import *
from db.__all_models import *
from db.db_session import create_sesion, init
from flask_login import login_required, LoginManager, login_user, logout_user, current_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()

login_manager.init_app(app)
app.secret_key = "123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
session = init("database.db")

auth_headers = []

@app.route("/")
@app.route("/home")
def index():
    try:
        if current_user.is_authenticated:
            return "You're log in"
        else:
            return render_template("base.html", title="beta v0.0.0")
    except:
        pass



@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    if form.is_submitted():
        session = create_sesion()

        userlog = session.query(User).filter(User.login == str(form.login.data)).first()
        hashed_password = userlog.password

        if bcrypt.check_password_hash(hashed_password, form.password.data):
            login_user(userlog)
            return redirect(url_for("chats"))
        flash("Неверный логин/пароль")
    return render_template("login.html", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if form.is_submitted() and form.password.data == form.repassword.data:
        session = create_sesion()
        new_user = User()
        new_user.login = form.login.data
        new_user.password = bcrypt.generate_password_hash(form.password.data)
        session.add(new_user)
        session.commit()
        login_user(new_user)
        session.close()
        return redirect(url_for("chats"))
    return render_template("register.html", form=form)

@app.route("/im/<int:cel>", methods=["POST", "GET"])
@login_required
def im(cel):
    session = create_sesion()
    session.add(current_user)
    session.flush()

    chat = session.query(Chat).filter(Chat.id == str(cel)).first()

    if not chat:
        return redirect(url_for("create_chat"))
    if not f";{current_user.id};" in chat.users:
        return "Вы не имеете доступа к данному чату"

    session.close()
    form = TextForm(request.form)
    if form.is_submitted():
        session = create_sesion()
        session.add(current_user)
        session.flush()

        message = Message()
        message.text = form.text.data
        message.user_id = current_user.id
        message.chat_id = cel

        session.add(message)
        session.commit()
        session.close()

    session = create_sesion()
    session.add(current_user)

    messages = session.query(Message).filter(Message.chat_id == int(cel)).all()
    session.flush()

    session.commit()
    return render_template("im.html", form=form, messages=messages, cel=cel)


@app.route("/chats/create_chat", methods=["POST", "GET"])
@login_required
def create_chat():
    form = ChatCreateForm()

    if form.is_submitted():
        session = create_sesion()
        session.add(current_user)
        session.flush()

        chat = Chat()
        chat.name = form.name.data
        chat.users = ";" + str(current_user.id) + ";"
        session.add(chat)
        session.commit()
        session.close()
        return redirect(url_for("chats"))
    return render_template("create_chat.html", form=form)


@app.route("/chats")
@login_required
def chats():
    session = create_sesion()
    session.add(current_user)
    session.flush()

    chats = session.query(Chat).filter(Chat.users.like(f"%;{current_user.id};%")).all()
    session.close()
    return render_template("chats.html", chats=chats)


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect("login")


@login_manager.user_loader
def load_user(user_id):
    try:
        session = create_sesion()
        user = session.query(User).get(int(user_id))
        session.commit()
        return user
    except:
        return


@app.route("/chats/invite/<int:cel>", methods=["POST", "GET"])
@login_required
def invite(cel):
    form = ChatInviteForm(request.form)
    if form.is_submitted():
        session = create_sesion()
        session.add(current_user)
        session.flush()

        current_chat = session.query(Chat).filter(Chat.id == int(cel)).first()

        if not f";{current_user.id};" in current_chat.users:
            return redirect(url_for("chats"))

        current_chat.users += f";{form.user_id.data};"
        session.commit()
        session.close()
    return render_template("invite.html", form=form)





if __name__ == "__main__":
    app.run("localhost", 8080)
