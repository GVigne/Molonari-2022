# Molonari
# MOnitoring LOcal des échanges NAppe-RIvière

## Objectif
Développer une chaîne d’acquisition depuis le capteur jusqu’au poste de contrôle pour le suivi des échanges entre un cours d'eau et une nappe afin de proposer des outils innovants de suivi de la ressource en eau

## Ressources
Dans le dossier ```ressources```, vous trouverez :
* la liste du matériel déployable calibré en laboratoire (dossier ```configuration```)
* la liste des points de mesures récoltés sur le terrain (dossier ```sampleing_points```)

## Module de calcul
Dans le dossier ```calcul```, vous trouverez le module python permettant de :
* Lancer le modèle physique 1D à partir d'un jeu de paramètres 
* Réaliser l'inférence des paramètres par inversion bayésienne

## Interface Homme-Machine
Dans le dossier ```ihm```, vous trouverez l'application graphique en python permettant de gérer une étude laquelle contient plusieurs points de mesures. Cette application nécessite l'installation du module de calcul.

## Etudes
Dans le dossier ```studies```, vous trouverez les études (bases de données) manipulées par l'IHM. Le format de la base de données dépend de la version de l'IHM utilisée. Ces études sont utiles pour tester et faire la démonstration de la chaine de traitement globale.

