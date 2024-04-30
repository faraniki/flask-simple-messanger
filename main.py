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

anonymous_headers = [{"url": "login",
                      "name": "login"},
                     {"url": "register",
                      "name": "register"}]

authorized_headers = [{"url": "logout",
                       "name": "log out"},
                      {"url": "chats",
                       "name": "chats"},
                      {"url": "create_chat",
                       "name": "create chat"}]


@app.route("/<login>", methods=["POST", "GET"])
def index(login):
    session = create_sesion()

    form = TextForm(request.form)
    user = session.query(User).filter(User.login == str(login)).first()
    session.close()

    if current_user.is_authenticated:
        session = create_sesion()

        session.add(current_user)
        session.flush()

        if form.is_submitted():
            post = Post()
            post.text = form.text.data
            post.user_login = current_user.login

            session.add(post)
            session.commit()
            session.close()
            return redirect(url_for("index", login=login))

        posts = session.query(Post).filter(Post.user_login == str(login)).all()
        return render_template("profile.html", title="beta v0.0.1", headers=authorized_headers, user=user, posts=posts, form=form, login=login)
    else:
        posts = session.query(Post).filter(Post.user_login == str(login)).all()

        return render_template("profile.html", title="beta v0.0.1", headers=anonymous_headers, user=user, posts=posts, form=form, login=login)




@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm(request.form)
    flash("Неверный логин/пароль")
    if form.is_submitted():
        session = create_sesion()
        userlog = session.query(User).filter(User.login == str(form.login.data)).first()
        session.close()
        if not userlog:
            flash("Неверный логин/пароль")
            return render_template("login.html", form=form)
        hashed_password = userlog.password

        if not bcrypt.check_password_hash(hashed_password, form.password.data):
            flash("Неверный логин/пароль")
            return redirect(url_for("login"))

        login_user(userlog)
        return redirect(url_for("chats"))
    return render_template("login.html", form=form, headers=anonymous_headers)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if form.is_submitted() and form.password.data == form.repassword.data:
        session = create_sesion()
        if session.query(User).filter(User.login == str(form.login.data)).first():
            session.close()
            return redirect(url_for("register"))
        new_user = User()
        new_user.login = form.login.data
        new_user.password = bcrypt.generate_password_hash(form.password.data)

        session.add(new_user)
        session.commit()
        session.close()

        return redirect(url_for("login"))
    return render_template("register.html", form=form, headers=anonymous_headers)


@app.route("/im/<int:cel>", methods=["POST", "GET"])
@login_required
def im(cel):
    session = create_sesion()
    session.add(current_user)
    session.flush()
    chat = session.query(Chat).filter(Chat.id == int(cel)).first()

    if not chat:
        session.close()
        return redirect(url_for("create_chat"))
    if not f";{current_user.id};" in chat.users:
        session.close()
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
        message.user_login = current_user.login
        message.chat_id = cel

        session.add(message)
        session.commit()
        session.close()
        return redirect(url_for('im', cel=cel))

    session = create_sesion()
    session.add(current_user)
    session.flush()

    messages = union_message(session.query(Message).filter(Message.chat_id == int(cel)).all())

    session.close()
    return render_template("im.html", form=form, messages=messages, cel=cel, headers=authorized_headers)


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
    return render_template("create_chat.html", form=form, headers=authorized_headers)


@app.route("/chats")
@login_required
def chats():
    session = create_sesion()
    session.add(current_user)
    session.flush()

    chats = session.query(Chat).filter(Chat.users.like(f"%;{current_user.id};%")).all()
    session.close()
    return render_template("chats.html", chats=chats, headers=authorized_headers)


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
        session.close()
        return user
    except:
        return


@app.route("/chats/invite/<cel>", methods=["POST", "GET"])
@login_required
def invite(cel):
    form = ChatInviteForm(request.form)
    if form.is_submitted():
        session = create_sesion()
        session.add(current_user)
        session.flush()

        current_chat = session.query(Chat).filter(Chat.id == int(cel)).first()

        if not f";{current_user.id};" in current_chat.users:
            session.close()
            return redirect(url_for("chats"))

        current_chat.users += f";{form.user_id.data};"
        session.commit()
        session.close()
    return render_template("invite.html", form=form, headers=anonymous_headers)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect("login")


def union_message(messages):
    result = []
    login = -1
    for message in messages:
        if message.user_login != login:
            result.append([])
        result[-1].append(message)
        login = message.user_login
    return result


if __name__ == "__main__":
    app.run("localhost", 8080)
