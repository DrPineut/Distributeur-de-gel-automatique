# !!!!!!!! installer les bibliothèques !!!!!!!

from raspisms import GsmModem                                                                                                       # Pour la gestion du modem GSM
import time
import RPi.GPIO as GPIO                                                                                                             # Pour la gestion des broches GPIO
import requests                                                                                                                     # Pour les requêtes HTTP
import logging
import csv
import json
import sys
import signal
import subprocess                                                                                                                   # Bibliothèque subprocess pour utiliser Gammu

# Constantes

IR_SENSOR_PIN = 17                                                                                                                  # Broche GPIO pour le capteur infrarouge
SERVO_PIN = 18                                                                                                                      # Broche GPIO pour le servo-moteur
MAX_GEL_CAPACITY = 300                                                                                                              # Capacité maximale du flacon de gel
CONFIG_FILE = "config.json"                                                                                                         # Fichier de configuration

# Variables Globales

gel_used = 0                                                                                                                        # Quantité de gel utilisée
hands_detected = 0                                                                                                                  # Nombre de mains détectées

# Initialisation des broches GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)                                                                                                     # Configuration de la fréquence du servo à 50 Hz
servo.start(0)                                                                                                                      # Position initiale du servo

# Fonction pour lire la configuration depuis config.json

def read_config():
    try:
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    except Exception as e:
        print(f"Erreur lors de la lecture de la configuration : {str(e)}")
        sys.exit(1)

# Validation de la configuration

def validate_config(config):
    required_keys = ["API_URL", "CSV_FILE", "MAX_RETRIES", "GEL_AMOUNT", "ALARM_PHONE_NUMBER"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"La clé de configuration '{key}' est manquante dans config.json")

# Fonction pour envoyer un SMS

def send_sms(phone_number, message, modem):
    try:
        modem.connect()
        #Attendre que le modem soit prêt
        time.sleep(1)
        modem.sms.send(phone_number, message)
        print("SMS envoyé avec succès.")
    except Exception as e:
        print (f"Erreur lors de l'envoi du sms : ", str(e))
    finally:
        modem.disconnect()

# Fonction pour activer le servo

def activate_servo():
    servo.ChangeDutyCycle(7.5)                                                                                                      # Angle du servo pour tourner
    time.sleep(1)
    servo.ChangeDutyCycle(0)                                                                                                        # Arrêter le servo

# Fonction pour écrire des données dans un fichier CSV

def write_data_to_csv(data, csv_file):
    try:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(data)
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier CSV : {str(e)}")

# Fonction pour envoyer les données au serveur

def send_data_to_server(amount, api_url, max_retries):
    data = {"gel_used": f"{amount} ml"}
    for retry in range (max_retries):
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                print("Données envoyées avec succès au serveur.")
                break                                                                                                               # Sortir de la boucle en cas de succès
            else:
                print(f"Erreur lors de l'envoi des données au serveur. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Erreur lors de la communication avec le serveur : {str(e)}")

        if retry < MAX_RETRIES - 1:
            print(f"Tentative de réessai {retry + 1} sur {max_retries}")
            time.sleep(2)
        else:
            print("Toutes les tentatives de réessai ont échoué.")

# Gestionnaire de signal pour une sortie propre

def signal_handler(sig, frame):
    print("Exiting...")
    servo.stop()
    GPIO.cleanup()
    sys.exit(0)

# Fonction principale

def main():
    global gel_used, hands_detected
    config = read_config()

# Validation de la configuration

    validate_config(config)

    modem = GsmModem(port="/dev/ttyUSB0", baudrate=9600)        # MODIFIER EN FONCTION DU VOTRE 

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while True:
            if GPIO.input(IR_SENSOR_PIN) == GPIO.HIGH:
                print("Main détectée. Activation du servo.")
                activate_servo()
                send_data_to_server(config["GEL_AMOUNT"], config["API_URL"], config["MAX_RETRIES"])                                 # Envoyer 3 ml au serveur

                gel_used += config["GEL_AMOUNT"]
                hands_detected += 1

                if gel_used >= MAX_GEL_CAPACITY:
                    print("La capacité maximale du flacon a été atteinte !")

# Utiliser Gammu pour envoyer un SMS
                    recipient_number = config["ALARM_PHONE_NUMBER"]
                    sms_message = "La capacité maximale du flacon a été atteinte !"
                    try:
                        subprocess.run(["gammu-sms-inject", "TEXT", recipient_number, "-text", sms_message])
                        print("SMS envoyé avec succès.")
                    except Exception as e:
                        print(f"Erreur lors de l'envoi du SMS : {str(e)}")

# Autres actions en cas d'alerte (enregistrement dans un journal, etc...)

                data_to_save = [gel_used, hands_detected]
                with open(config["CSV_FILE"], mode='a', newline='') as csv_file:
                    write_data_to_csv(data_to_save, csv_file)

                print(f"Total de gel utilisé : {gel_used} ml")
                print(f"Total de mains détctées : {hands_detected}")

            time.sleep(0.1)                                                                                                         # Attente pour éviter la détection multiple

    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
