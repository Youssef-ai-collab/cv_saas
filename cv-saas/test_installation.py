try:
    import flask
    import nltk
    import spacy
    import stripe
    import PyPDF2
    from docx import Document
    print("✅ Toutes les dépendances sont installées avec succès!")
except ImportError as e:
    print(f"❌ Erreur: {e}")