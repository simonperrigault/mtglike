# mtglike

## Explications

MTGLike est un projet que j'ai effectué durant un stage à Météo France.
Avec la mise en place des satellites de 3ème génération (MTG), nous devions faire la transition entre ceux-ci et les satellites de 2ème génération (MSG).
Nous savions que les MTG avaient besoin de temps de pause au départ pour effectuer des ajustements.
Nous devions donc simuler des données de MTG (plus fréquente, plus précise...) avec des données de MSG.
Le plus grand défi que nous nous étions donné avec mon binôme était d'extrapoler les images de MTG avec celles de MSG.
Par exemple, MTG arrive à 12h00, 12h10 et 12h20 alors que MSG seulement à 12h00, 12h15 et 12h30.
Quelle image donner à 12h20 pour des clients qui attendent une image MTG et qui ne doivent pas voir la différence ?
Nous avons donc essayer de calculer le champ d'advection entre les 2 images précédentes afin de l'appliquer sur l'image la plus récente pour extrapoler notre image de 12h20.

## Use

Dependencies :
- gdal
- pyinotify
- xarray

Useful commands :
- to clean the folders : find automate \( -type f -o -type l \) -delete
- to start the script : python3 event_handler.py
- to create a link and start the process (on another terminal) : ln -s /path/to/file.nc automate/reception/
