import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        return False

print("Installation des dépendances manquantes...")

packages_to_install = ["flask", "python-dotenv", "nltk", "spacy", "stripe", "PyPDF2", "python-docx"]

for package in packages_to_install:
    print(f"Installation de {package}...")
    if install_package(package):
        print(f"✅ {package} installé")
    else:
        print(f"❌ Échec installation de {package}")

print("Téléchargement des données NLTK...")
try:
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    print("✅ Données NLTK téléchargées")
except Exception as e:
    print(f"❌ Erreur NLTK: {e}")