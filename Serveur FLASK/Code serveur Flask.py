from flask import Flask, jsonify, request, make_response      # Import de Flask pour la création de l'application WEB
from flask_cors import CORS, cross_origin

app = Flask(__name__)    # Création d'une instance de l'application Flask
CORS(app, resources={r"/*": {"origins": "*"}})

# Données d'utilisation initiales (mis à jour par la suite)
data = {"gel_used": 0, "hands_detected": 0}  # Utiliser des valeurs numériques pour les données

# Route pour obtenir les données d'utilisations (une requête GET)
@app.route('/obtenir_donnees_utilisation', methods=['GET'])
@cross_origin()
def obtenir_donnees_utilisation():
  print("Données renvoyées par le serveur Flask :", data)
  return jsonify(data)  # Renvoie les données au format JSON dans un tableau

# Pour mettre à jour les données depuis le Raspberry Pi (une requête POST)
@app.route('/mettre_a_jour_donnees', methods=['GET', 'POST'])
def mettre_a_jour_donnees():
  global data    # Utilise la variable globale 'data' pour stocker les données

  if request.method == 'POST':
    try:
  
      # Récuperer les données envoyés par le Raspberry Pi au format JSON
      new_data = request.json

      print("Données reçues depuis Postman :")
      print(new_data)

      gel_used = data["gel_used"]
      hands_detected = data["hands_detected"]

      gel_used += new_data.get("gel_used", 0)
      hands_detected += new_data.get("hands_detected", 0)

      data["gel_used"] = gel_used
      data["hands_detected"] = hands_detected

      response_body = "Données mise à jour avec succès"
      response_status = 200
      response_headers = {'Content-Type': 'text/plain'}
  
      return response_body, response_status, response_headers

    except Exception as e:
      response_body = f"Erreur lors de la mise à jour des données : {str(e)}"
      response_status = 500
      response_headers = {'Content-Type': 'text/plain'}

      return response_body, response_status, response_headers
  
  # Si la méthode est GET
  return "Requête GET reçue avec succès"

@app.route('/')
@cross_origin()
def welcome():
  return "Bienvenue sur votre serveur Flask !"

@app.route('/*', methods=['OPTIONS'])
@cross_origin()
def handle_options():
  response = make_response()
  response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
  return response

@app.route('/pourcentage_restant', methods=['GET'])
@cross_origin()
def pourcentage_restant():
  capacite_totale = 300
  gel_utilise = data["gel_used"]

  if capacite_totale > 0:
    pourcentage = (1 - gel_utilise / capacite_totale) * 100
  else:
    pourcentage = 0
  
  return jsonify({"pourcentage_restant": pourcentage})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)    # Démarrage de l'application Flask sur l'adresse IP '0.0.0.0' et le port 5000
