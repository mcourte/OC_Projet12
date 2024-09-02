# Projet 12 : Développez une architecture back-end sécurisée avec Python et SQL



## Etape 1 : Télécharger le code

Cliquer sur le bouton vert "<> Code" puis sur Download ZIP.  
Extraire l'ensemble des éléments dans le dossier dans lequel vous voulez stockez les datas qui seront téléchargées.  


## Etape 2 ; Installer Python et ouvrir le terminal de commande

Télécharger [Python](https://www.python.org/downloads/) et [installer-le](https://fr.wikihow.com/installer-Python)  

Ouvrir le terminal de commande :  
Pour les utilisateurs de Windows : [démarche à suivre ](https://support.kaspersky.com/fr/common/windows/14637#block0)  
Pour les utilisateurs de Mac OS : [démarche à suivre ](https://support.apple.com/fr-fr/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac)  
Pour les utilisateurs de Linux : ouvrez directement le terminal de commande   


## Etape 3 : Création de l'environnement virtuel

Se placer dans le dossier où l'on a extrait l'ensemble des documents grâce à la commande ``cd``  
Exemple :
```
cd home/magali/OpenClassrooms/Formation/Projet_12
```


Dans le terminal de commande, executer la commande suivante :
```
python3 -m venv env
```


Activez l'environnement virtuel
```
source env/bin/activate
```
> Pour les utilisateurs de Windows, la commande est la suivante : 
> ``` env\Scripts\activate.bat ```

## Etape 4 : Télécharger les packages nécessaires au bon fonctionnement du programme


Installez ensuite les packages requis:  
```
pipenv install -r requirements.txt
```

## Etape 5 : Lancer le programme


Depuis le terminal de commande, tapez la commande suivante :
```
python3 main.py start
```
Des identifiants de connexion vous seront demandés:  
Plusieurs possibilités s'offrent à vous suivant le rôle que vous souhaitez avoir 

|   Nom d'utilisateur   |   Mot de passe |   Rôle |
|---    |:-:    |:-:    |
|   mcourte |   password   |   Admin |
|   jcourte   |   password |   Commercial|
|   mthomas   |   password   |   Gestion 
|   idavid   |   password  |   Support |


## Etape 6 : L'application

* Le menu varie en fonction du rôle de l'utilisateur
* La base de données contient déjà quelques clients, contrats & évenèments pour que vous puissez tester chaque fonction
