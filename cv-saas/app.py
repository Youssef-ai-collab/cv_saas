from flask import Flask, render_template, request, session, redirect, url_for
import os
import secrets
import re
from datetime import datetime, timedelta
import json


# Configuration directe
class Config:
    SECRET_KEY = 'cv_saas_super_secret_key_2024_123!'
    STRIPE_PUBLIC_KEY = 'pk_test_51SWdoHRbTGOIXLwnCTYoc2Aq3pkySs2rFBcXQNcqt8Ey5hsEjESFvfPElz1b5vF8GgWYUZTZ3ZT2AoXKPqAES0TF00M3ZAvVEz'
    STRIPE_SECRET_KEY = 'sk_test_51SWdoHRbTGOIXLwnhFbcbVgHdZzgsIKsWz0tvdCxfH30qXy7mr7DBIZKcwGSOaavQAMx6BQbh5wKVlXIJvRNrb1n00wkqkv6mD'
    OPENAI_API_KEY = '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'


app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Fichier pour stocker les utilisateurs
USERS_FILE = 'users.json'


def load_users():
    """Charge les utilisateurs depuis le fichier JSON"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Erreur chargement utilisateurs: {e}")
        return {}


def save_users(users):
    """Sauvegarde les utilisateurs dans le fichier JSON"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde utilisateurs: {e}")
        return False


# Charger les utilisateurs au démarrage
users = load_users()

if not os.path.exists('uploads'):
    os.makedirs('uploads')


def is_student_email(email):
    """Vérifie si l'email est un email étudiant"""
    return email.endswith('@etu.uae.ac.ma')


def parse_datetime(dt_string):
    """Parse une date string en objet datetime de manière sécurisée"""
    if not dt_string or not isinstance(dt_string, str):
        return None
    try:
        return datetime.fromisoformat(dt_string)
    except (ValueError, TypeError):
        return None


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Recharger les utilisateurs à chaque connexion
        users = load_users()

        # Vérification
        if email in users and users[email]['password'] == password:
            session['user'] = users[email]
            session['free_used'] = users[email].get('free_used', False)
            session['premium'] = users[email].get('premium', False)
            session['student'] = users[email].get('student', False)
            session['premium_until'] = users[email].get('premium_until')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Email ou mot de passe incorrect")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérifier que tous les champs sont remplis
        if not all([fullname, email, password]):
            return render_template('signup.html', error="Tous les champs sont obligatoires")

        # Recharger les utilisateurs
        users = load_users()

        if email in users:
            return render_template('signup.html', error="Un compte avec cet email existe déjà")

        # Vérifier si c'est un email étudiant
        student = is_student_email(email)

        # Création de l'utilisateur
        users[email] = {
            'fullname': fullname,
            'email': email,
            'password': password,
            'free_used': False,
            'premium': student,  # Les étudiants ont premium gratuit
            'student': student,
            'premium_until': None,
            'created_at': datetime.now().isoformat()
        }

        if student:
            # Ajouter 1 an de premium gratuit pour les étudiants
            users[email]['premium_until'] = (datetime.now() + timedelta(days=365)).isoformat()

        # Sauvegarder les utilisateurs
        if save_users(users):
            session['user'] = users[email]
            session['free_used'] = False
            session['premium'] = student
            session['student'] = student
            session['premium_until'] = users[email].get('premium_until')

            return redirect(url_for('dashboard'))
        else:
            return render_template('signup.html', error="Erreur lors de la création du compte")

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Vérifier si le premium étudiant est toujours valide
    if session.get('student') and session.get('premium_until'):
        premium_until = parse_datetime(session['premium_until'])
        if premium_until and datetime.now() > premium_until:
            # Le premium étudiant a expiré
            session['premium'] = False
            users = load_users()
            if session['user']['email'] in users:
                users[session['user']['email']]['premium'] = False
                save_users(users)

    return render_template('dashboard.html')


@app.route('/abonnement')
def abonnement():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('subscription'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_cv():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Vérifier si l'utilisateur a utilisé son essai gratuit ou s'il n'est pas premium
        if session.get('free_used') and not session.get('premium'):
            return redirect(url_for('subscription'))

        if 'cv' not in request.files:
            return render_template('upload.html', error="Aucun fichier sélectionné")

        file = request.files['cv']
        if file.filename == '':
            return render_template('upload.html', error="Aucun fichier sélectionné")

        if file:
            allowed_extensions = ['pdf', 'docx', 'txt']
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return render_template('upload.html', error="Format non supporté. Utilisez PDF, DOCX ou TXT.")

            try:
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                from utils.cv_analyzer import analyze_cv_with_openai
                analysis_result = analyze_cv_with_openai(file_path)

                if os.path.exists(file_path):
                    os.remove(file_path)

                # Marquer l'essai gratuit comme utilisé
                if not session.get('premium'):
                    session['free_used'] = True
                    users = load_users()
                    if session['user']['email'] in users:
                        users[session['user']['email']]['free_used'] = True
                        save_users(users)

                return render_template('results.html', results=analysis_result)

            except Exception as e:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
                return render_template('upload.html', error=f"Erreur: {str(e)}")

    return render_template('upload.html')


@app.route('/subscription')
def subscription():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('subscription.html')


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session_route():
    if 'user' not in session:
        return redirect(url_for('login'))

    subscription_type = request.form.get('subscription_type', 'monthly')

    try:
        from utils.payment_handler import create_checkout_session
        checkout_session = create_checkout_session(subscription_type)
        return redirect(checkout_session.url)
    except Exception as e:
        return render_template('subscription.html', error=f"Erreur de paiement: {str(e)}")


@app.route('/success')
def success():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Récupérer le type d'abonnement depuis l'URL
    subscription_type = request.args.get('type', 'monthly')

    # Marquer l'utilisateur comme premium
    session['premium'] = True

    # Définir la durée du premium
    if subscription_type == 'yearly':
        premium_until = datetime.now() + timedelta(days=365)
    else:
        premium_until = datetime.now() + timedelta(days=30)

    # Sauvegarder dans la base
    users = load_users()
    if session['user']['email'] in users:
        users[session['user']['email']]['premium'] = True
        users[session['user']['email']]['premium_until'] = premium_until.isoformat()
        save_users(users)

    session['premium_until'] = premium_until.isoformat()

    return render_template('success.html', subscription_type=subscription_type)


@app.route('/cancel')
def cancel():
    return redirect(url_for('subscription'))


@app.route('/reset')
def reset():
    # Pour les tests seulement
    if 'user' in session:
        session['free_used'] = False
        users = load_users()
        if session['user']['email'] in users:
            users[session['user']['email']]['free_used'] = False
            save_users(users)
    return redirect(url_for('dashboard'))


@app.route('/admin/users')
def admin_users():
    # Page admin pour voir les utilisateurs (pour debug)
    users = load_users()
    return f"""
    <h1>Utilisateurs ({len(users)})</h1>
    <pre>{json.dumps(users, indent=2, ensure_ascii=False)}</pre>
    <a href="/dashboard">Retour</a>
    """


@app.errorhandler(413)
def too_large(e):
    return render_template('upload.html', error="Fichier trop volumineux. Max: 16MB")


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)