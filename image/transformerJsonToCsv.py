"""Travail du groupe: Elloit Paillat--Garcia et Titouan Leblanc--Floch """

#importation de toute les bibliothèques à utiliser .

import re
from html import unescape
import csv
import json


def nettoyer_html(texte):
   """ Nettoie le texte des balises HTML et des entités HTML."""   
   if texte:
        texte = unescape(texte)  # Décoder les entités HTML.
        texte = re.sub(r'<[^>]+>', '', texte)  # Supprimer les balises HTML.
        return texte.strip()  # Supprimer les espaces non important.
   return "Non disponible"



def transformelefichier(a :str):
    """Transformation du fichier json en fichier csv"""
    
    if a.strip().lower() == "oui":  
        
        try :
            
             liste = ["ID", "URL", "Titre", "Chapeau", "Description", "Mots clés",
                      "Date de début", "Heure de début", "Date de fin", "Heure de Fin",
                      "Nom du lieu", "Adresse du lieu", "Code Postal", "Ville", 
                      "Coordonnées géographiques","Accès PMR", "Accès mal voyant", 
                      "Accès mal entendant", "Transport","Nom de contact", "Téléphone de contact", 
                      "Email de contact", "Url de contact","Type d’accès", "Détail du prix", 
                      "URL de l’image de couverture"]#Création d'une liste qui contient tout les termes à chercher . 
             
             dico ={} #Création d'un dico pour tout les elements .
             f1 = open("que-faire-a-paris-.json","r", encoding="utf-8")#Ouverture du fichier json .
             contenu = json.load(f1) 
             
             f2 = open("que-faire-a-paris-.csv","wt",encoding = "utf-8-sig", newline='')#Ouverture d'un fichier csv vierge . 
             ecrireCSV = csv.DictWriter(f2,fieldnames=liste,delimiter=";")
             ecrireCSV.writeheader()    # On écrit la ligne d'en-tête avec le titre des colonnes .
             
             for event in contenu :
                 mots_cles = event.get("tags", [])
                 if not isinstance(mots_cles, list):  # Vérifie que "tags" est une liste
                     mots_cles = [mots_cles] if mots_cles else []
                     
                 #Calcul des latitudes et longitudes des évènements .   
                 lat_lon = event.get('lat_lon')
                 latitude = event.get('lat_lon', {}).get('lat', '') if lat_lon else ''
                 longitude = event.get('lat_lon', {}).get('lon', '') if lat_lon else ''

                 #dico qui se remplie a chaque évènements avec les élemments de la liste .
                 #utilisation du get pour trouver tout les imformations si non trouverremplacer par : Non disponible . 
                 dico = {
                     "ID": event.get("id", "Non disponible"),
                     "URL": event.get("url", "Non disponible"),
                     "Titre": nettoyer_html(event.get("title", "Non disponible")),
                     "Chapeau": nettoyer_html(event.get("lead_text", "Non disponible")),
                     "Description": nettoyer_html(event.get("description", "Non disponible")),
                     "Mots clés": ", ".join(mots_cles),
                     "Date de début": event.get("date_start", "Non disponible").split("T")[0] if event.get("date_start") else "Non disponible",
                     "Heure de début": event.get("date_start", "Non disponible").split("T")[1][:5] if event.get("date_start") else "Non disponible",
                     "Date de fin": event.get("date_end", "Non disponible").split("T")[0] if event.get("date_end") else "Non disponible",
                     "Heure de Fin": event.get("date_end", "Non disponible").split("T")[1][:5] if event.get("date_end") else "Non disponible",
                     "Nom du lieu": nettoyer_html(event.get("address_name", "Non disponible")),
                     "Adresse du lieu": nettoyer_html(event.get("address_street", "Non disponible")),
                     "Code Postal": event.get("address_zipcode", "Non disponible"),
                     "Ville": nettoyer_html(event.get("address_city", "Non disponible")),
                     "Coordonnées géographiques": f"{latitude}, {longitude}",
                     "Accès PMR": "Oui" if event.get("pmr") == 1 else "Non",
                     "Accès mal voyant": "Oui" if event.get("blind") else "Non",
                     "Accès mal entendant": "Oui" if event.get("deaf") else "Non",
                     "Transport": nettoyer_html(event.get("transport", "Non disponible")),
                     "Nom de contact": nettoyer_html(event.get("contact_name", "Non disponible")),
                     "Téléphone de contact": event.get("contact_phone") or "Non disponible",
                     "Email de contact": event.get("contact_mail") or "Non disponible",
                     "Url de contact": event.get("contact_url") or "Non disponible",
                     "Type d’accès": event.get("access_type", "Non disponible"),
                     "Détail du prix": nettoyer_html(event.get("price_detail", "Non disponible")),
                     "URL de l’image de couverture": event.get("cover_url", "Non disponible")
                 }
                 
                 ecrireCSV.writerow(dico)#Écrit le dico en csv 
                 
             print("Le fichier JSON à bien été transformé en fichier csv avec comme nom : que-faire-a-paris-.csv , dans la même partie que le code python ,vous pouvez ouvrir directement le fichier depuis le document ou pour de la propreté ouvrir le fichier csv directement dans Excel .")
             
        #Création de tout les excepts eurreur que peut rencontrer l'utilisateur . 
        
        except FileNotFoundError:
         """le fichier est introuvable"""
         print("Fichier introuvable ou alors se n'est pas le bon .")
             
        except Exception as e:
            print(f"Une erreur inattendue s'est produite : {e}")  
            
        except json.JSONDecodeError:
            """Indique que lors de lannalyse des données certaine sont mal formatées """
            print("Le fichier JSON est mal formé(Vérifier et valider les données JSON avant de les utiliser).")
            
        except PermissionError:
            """Indique à l'utilisateur que le fichier est déja ouvert et qu'il ne peut pas en regénérer un autre """
            print("Le fichier Excel doit être déja ouvert.")
            
        finally:
             f1.close()#fermetur du fichier 1(json) .
             f2.close()#fermetur du fichier 2(csv) . 
    else:
        print("Vous avez annulée l'action.")#indique que l'utilisateur à annulé la transformation . 
        
       
"""Programme principal"""      

h="Pour modifier votre fichier ecrivez :transformelefichier('oui')"#initialise le message à print pour le programme principal .
print(h)

