from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlite3 import *
from datetime import datetime, timedelta, date
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JHKPJdhqpsdhIPQHSDKJHIhDKJhkjh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                                    'production.db')
db = SQLAlchemy(app)
scheduler = BackgroundScheduler()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'connexion'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Initialize database
with app.app_context():
    db.create_all()


# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=150)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=150)])
    submit = SubmitField('Login')


def get_username_by_id(user_id):
    user = db.session.get(User, user_id)
    if user:
        return user.username
    return None


def exec_sql(query, params=()):
    try:
        # Connect to SQLite database
        conn = connect("production.db")
        cursor = conn.cursor()

        # Execute the query with the provided parameters
        cursor.execute(query, params)

        # Commit the transaction
        conn.commit()
        result = cursor.fetchall()
        if conn:
            conn.close()
        return result
    except Error as e:
        print(query)
        print(f"Error executing query: {e}")
        return False


def check_chambre(num: int) -> bool:
    conn = connect("production.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT ID FROM Chambre WHERE id = {num};")
    result = cursor.fetchall()
    conn.close()
    return result


def check_room_availability(start_date, end_date):
    query = """
    SELECT Categorie
    FROM Chambre
    WHERE ID NOT IN (
        SELECT Chambre
        FROM Réservation
        WHERE (
                strftime('%Y-%m-%d', Arrivé) <= ? AND strftime('%Y-%m-%d', Départ) >= ?
            )
            OR (
                strftime('%Y-%m-%d', Arrivé) <= ? AND strftime('%Y-%m-%d', Départ) >= ?
            )
            OR (
                strftime('%Y-%m-%d', Arrivé) >= ? AND strftime('%Y-%m-%d', Départ) <= ?
            )
    )
    """

    query = """
        
            SELECT Chambre
            FROM Réservation
            WHERE (
                    strftime('%Y-%m-%d', Arrivé) <= ? AND strftime('%Y-%m-%d', Départ) >= ?
                )
                OR (
                    strftime('%Y-%m-%d', Arrivé) <= ? AND strftime('%Y-%m-%d', Départ) >= ?
                )
                OR (
                    strftime('%Y-%m-%d', Arrivé) >= ? AND strftime('%Y-%m-%d', Départ) <= ?
                )
        
        """

    params = (start_date, start_date, end_date, end_date, start_date, end_date)
    available_rooms = exec_sql(query, params)
    print(available_rooms)
    return [{'type': room[0]} for room in available_rooms]


def send_email(sender_email, sender_password, receiver_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attachement du corps du message à l'objet MIMEText
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connexion au serveur SMTP (par exemple, Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Envoi de l'email
        server.send_message(msg)
        server.quit()

        print("Email envoyé avec succès!")
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False


def mail_automatique():
    sender_email, sender_password, receiver_email, subject, body = [_ for _ in range(5)]


@app.route('/email', methods=['GET', 'POST'])
@login_required
def email():
    if request.method == "POST":
        pass
    email = 'maixins@gmail.com'
    msg = """Bonjour,
     Menu du jour:
     Pain au chocolat: 1, croissant : 1, baguette: 1 
     Nombre de menu : / inserer le nombre avec la base de donnée /
     
     
     """
    obj = "Commande "
    return render_template("email.html",email=email,msg=msg,obj=obj)


@app.route('/sql', methods=['GET', 'POST'])
@login_required
def sql_urgence():
    info = None
    if request.method == "POST":
        query = dict(request.form)["query"]
        info = {"request": exec_sql(query)}
    return render_template("sql_urgence.html", info=info)


@app.route('/')
@login_required
def index():
    id = current_user.get_id()
    nom = get_username_by_id(id)
    return render_template("index.html", info={"nom": nom})


@app.route('/dashboard')
@login_required
def dashboard():
    id = current_user.get_id()
    nom = get_username_by_id(id)
    return render_template("dashboard.html", info={"nom": nom})


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('connexion'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='scrypt')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('connexion'))
    else:
        if request.method == 'POST':
            flash('Error in form submission. Please check your inputs.', 'error')
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('connexion'))


@app.route("/chambre", methods=["POST", "GET"])
@login_required
def chambre():
    if request.method == 'POST':
        form = dict(request.form)
        print(form)
        if 'simple_beds' in form:
            table_name = "CatChambre"
            args = list(form.values())
            placeholders = ', '.join([f"'{arg}'" for arg in args])  # Placeholders for the values
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"

            err = exec_sql(query)
            if err is False:
                flash("La catégorie a eu un probleme lors de sa création", "error")
            else:
                flash("La catégorie a été créée.", "success")
        elif "action" in form:

            if "room_id" in form:
                print("deleting chambre")
                query = f"DELETE FROM Chambre WHERE id = {form['item_id']};"
            else:
                print('deleting catégorie')
                query = f"DELETE FROM CatChambre WHERE Nom = '{form['item_id']}';"
            print(query)
            exec_sql(query)
        else:
            table_name = "Chambre"
            args = list(form.values())
            args.append(1)
            placeholders = ', '.join([f"'{arg}'" for arg in args])  # Placeholders for the values
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"

            print(query)
            err = exec_sql(query)
            if err is False:
                flash("La chambre a eu un probleme lors de sa création", "error")
            else:
                flash("La chambre a été créée.", "success")

    query1 = "SELECT * FROM Chambre"
    result1 = exec_sql(query1)
    query2 = "SELECT * FROM CatChambre"
    result2 = exec_sql(query2)
    print(result1)
    print(result2)
    info = {"chambres": result1, "catégorie": result2}
    return render_template("chambre.html", info=info)


@app.route('/get_reservations')
def get_reservations_route():
    room_id = request.args.get('room_id')
    reservations = exec_sql(f"SELECT * FROM Réservation WHERE Chambre = {room_id}")
    events = []
    print(reservations)
    for reservation in reservations:
        start_date = reservation[4]
        end_date = reservation[5]
        res = exec_sql(f"""
                            SELECT Nom, Prenom 
                            FROM Client 
                            JOIN 'Réservation' ON Client.ID = Réservation.client 
                            WHERE Client.ID = {reservation[2]}
                            """
                       )
        if len(res) > 0:
            nom, prénom = res[0]
        else:
            nom, prénom = "Client", "introuvable"

        # Convertir les dates de chaîne en objets datetime
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

        # Ajouter un jour à la date de fin
        end_datetime += timedelta(days=1)

        # Convertir les objets datetime en chaînes de nouveau au format 'YYYY-MM-DD'
        start_date = start_datetime.strftime('%Y-%m-%d')
        end_date = end_datetime.strftime('%Y-%m-%d')

        events.append({
            'title': f"{nom} {prénom}",
            'id': str(reservation[0]),
            'start': start_date,
            'end': end_date
        })

    return jsonify(events)


@app.route('/reservation')
@login_required
def reservation():
    # Récupérer les clients
    clients_query = "SELECT Nom, Prenom, Date FROM Client"
    info = {"clients": exec_sql(clients_query)}

    # Récupérer les catégories de chambres
    room_categories_query = "SELECT Nom FROM CatChambre"
    room_categories = exec_sql(room_categories_query)
    rooms = [room[0] for room in room_categories]
    info['room_categories'] = rooms

    # Récupérer les réservations futures
    future_reservations_query = """
        SELECT r.ID, r.Date, r.Arrivé, r.Départ, c.Nom || ' ' || c.Prenom AS client
        FROM Réservation r
        JOIN Client c ON r.Client = c.ID
        WHERE r.Départ >= DATE('now')
        """

    reservations_futures = exec_sql(future_reservations_query)
    info['reservations_futures'] = [
        {
            'id': res[0],
            'date_reservation': res[1],
            'start_date': res[2],
            'end_date': res[3],
            'client': res[4]
        }
        for res in reservations_futures]

    return render_template("reservation.html", info=info)


@app.route('/suppr_reservation')
@login_required
def suppr_reservation():
    reservation_id = request.args.get('id')
    if reservation_id:
        delete_query = "DELETE FROM Réservation WHERE ID = ?"
        exec_sql(delete_query, (reservation_id,))
        return redirect(url_for('reservation'))
    else:
        return "ID de réservation manquant", 400


@app.route('/client', methods=["POST"])
def add_client():
    form_data = request.form
    nom = form_data.get('nom')
    prenom = form_data.get('prenom')
    date_naissance = form_data.get('date_naissance')
    lieu_naissance = form_data.get('lieu_naissance')
    num_tel = form_data.get('num_tel')
    mail = form_data.get('mail')
    query = f"""
        INSERT INTO Client (Nom, Prenom, Date, Lieu, Tel, Mail)
        VALUES ('{nom}', '{prenom}', '{date_naissance}', '{lieu_naissance}', '{num_tel}', '{mail}');
        """
    exec_sql(query)
    return redirect("reservation")


@app.route('/search_client', methods=["GET"])
def search_client():
    query = request.args.get('query', '')
    res = query.split(' ')
    if len(res) > 1:
        nom, prenom = res
    else:
        nom = query
        prenom = ""
    print(nom, prenom)
    # Requête SQL pour chercher les clients correspondant au nom et prénom
    query = """
    SELECT * FROM Client
    WHERE nom LIKE ? AND prenom LIKE ?
    """
    params = ('%' + nom + '%', '%' + prenom + '%')

    clients = exec_sql(query, params)

    # Formater les résultats pour les envoyer en JSON
    formatted_clients = []
    for client in clients:
        formatted_client = {
            'id': client[0],
            'nom': client[1],
            'prenom': client[2],
            'date_naissance': client[3],
            'lieu_naissance': client[4],
            'num_tel': client[5],
            'mail': client[6]
        }
        formatted_clients.append(formatted_client)

    return jsonify(formatted_clients)


@app.route('/reserve_room', methods=["POST"])
def reserve_room():
    client_id = request.form.get('client_id')
    room_id = request.form.get('room_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    formatted_start_date = start_date
    formatted_end_date = end_date

    query = """
        INSERT INTO Réservation (Chambre, Client, Date, Arrivé, Départ)
        VALUES (?, ?, ?, ?, ?)
        """
    params = (room_id, client_id, date.today().strftime('%Y-%m-%d'), formatted_start_date, formatted_end_date)
    exec_sql(query, params)

    return f"Chambre {room_id} réservée pour le client {client_id} du {start_date} au {end_date}"


@app.route('/check_availability', methods=["POST"])
def check_availability():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Vérifier la disponibilité des chambres
    available_rooms = check_room_availability(start_date, end_date)
    print(available_rooms)

    # Retourner les types de chambres disponibles
    return jsonify(available_rooms)


@app.route('/select_room', methods=["GET"])
def select_room():
    client_id = request.args.get('client_id')
    query = "SELECT Nom FROM CatChambre"
    room_categories = exec_sql(query)
    return render_template('select_room.html', client_id=client_id, room_categories=room_categories)


@app.route('/get_tasks')
@login_required
def get_tasks():
    user = current_user.get_id()
    user = get_username_by_id(user)
    query = f"SELECT ID, Nom, Description, Date FROM Tache WHERE ID_user = '{user}'"
    tasks = exec_sql(query)
    tasks_list = [{
        'id': task[0],
        'title': task[1],
        'description': task[2],
        'start': task[3],
        'end': task[3]  # Assuming the task ends the same day it starts
    } for task in tasks]
    return jsonify(tasks_list)


@app.route("/edt", methods=["GET"])
@login_required
def edt():
    personnels = exec_sql(f"SELECT username FROM user")
    personnels = [personnel[0] for personnel in personnels]
    info = {"personnels": personnels}
    tasks = get_tasks()
    return render_template('edt.html', info=info, tasks=tasks)


@app.route('/add_task', methods=["POST"])
@login_required
def add_task():
    form = dict(request.form)
    nom = form['taskTitle']
    description = form['description']
    date = form["date"]
    personnel = form["employee"]

    query = f"INSERT INTO Tache (ID_user, Nom, Description, Date) Values ( '{personnel}', '{nom}', '{description}', '{date}' ) "
    exec_sql(query)
    return redirect("edt")


@app.route('/update_task_date', methods=['POST'])
def update_task_date():
    task_id = request.form.get('taskId')
    new_date = request.form.get('date')
    print(task_id, new_date)
    query = f"UPDATE Tache SET date = '{new_date}' WHERE ID = {task_id};"
    res = exec_sql(query)
    if res is not False:
        return jsonify({"message": "Date de la tâche mise à jour avec succès."}), 200
    else:
        return jsonify({"error": "La query SQL n'a pas fonctionnée "}), 500


@app.route('/delete_task', methods=['POST'])
@login_required
def delete_task():
    task_id = request.form.get('taskId')
    query = f"DELETE FROM Tache WHERE ID = {task_id} ;"
    exec_sql(query)
    return jsonify({'message': 'Tâche supprimée avec succès.'})


if __name__ == "__main__":
    try:
        scheduler.add_job(mail_automatique, 'cron', hour=1, minute=0)
        app.run(port=80, debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
