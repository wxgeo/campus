
Campus
======

Campus permet de publier simplement sous forme de site HTML statique une arborescence de fichiers indexée par git, avec éventuellement un peu de mise en forme.
Il est pensé comme un système de publications de cours notamment.
L’idée est de pouvoir très rapidement mettre à jour le contenu, tout en profitant des avantages de git, notamment :

- versioning ;
- possibilité de créer des branches (par exemple pour commencer à travailler sur le cours de l’année prochaine).

Pour ce faire, chaque dossier contiendra un fichier Markdown index.md, qui permettra de générer un fichier HTML.
Ce fichier index.md peut contenir simplement la liste des fichiers à indexer, toute l’interface de navigation étant générée automatiquement, mais on peut aussi du contenu. Exemple :

    # DUT Info
    Cette page regroupe mes cours de DUT Info 1<sup>re</sup> année.
    
    [M115 Documents numériques](M115-webdoc)
    
    [M121 Mathématiques Discrètes](M121-mathematiques_discretes)
    
    [M122 Algèbre linéaire](M122-algebre_lineaire)
    
    
Ensuite, il suffira d’exécuter la commande `campus push` pour générer le site web et le publier. 
