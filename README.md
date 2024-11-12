# JobGestion

JobGestion est une application MacOS simple permettant de gérer vos candidatures d'emploi. Conçue en Python, elle offre une interface utilisateur conviviale qui vous permet d'enregistrer, de modifier, de visualiser, et de supprimer vos candidatures. Les candidatures sont stockées localement au format JSON, ce qui garantit la confidentialité des informations.

## Fonctionnalités

- **Gestion des candidatures** : Ajoutez des informations telles que le nom de l'entreprise, le poste, la lettre de motivation, le statut de la candidature, des commentaires, etc.
- **Visualisation des candidatures** : Une interface claire pour voir toutes vos candidatures en un coup d'œil.
- **Modification et suppression** : Accédez à chaque candidature pour la mettre à jour ou la supprimer.
- **Commentaires** : Ajoutez des notes sur chaque candidature avec une limite de 1500 caractères.

## Installation

### Prérequis

- **Python 3.7+**
- **Tkinter** (inclus avec Python standard)
- **Pillow** pour la manipulation des images

Assurez-vous d'avoir Python installé sur votre système. Vous pouvez vérifier cela avec :

```bash
python --version
```

### Dépendances

Installez les dépendances requises en utilisant `pip` :

```bash
pip install Pillow
```

### Génération de l'application MacOS

Pour créer l'application MacOS, nous allons utiliser **PyInstaller**.

1. Installez PyInstaller :

   ```bash
   pip install pyinstaller
   ```

2. Générez le fichier `.app` avec la commande suivante :
   ```bash
   pyinstaller --windowed --onefile --add-data "app_logo.png:." --icon "logo.icns" job_gestion.py
   ```
   RE
3. Après l'exécution de cette commande, vous trouverez l'application dans le dossier `dist/`.

### Lancer l'application

Pour ouvrir l'application directement après génération :

```bash
./dist/job_gestion.app/Contents/MacOS/job_gestion
```

Pour lancer l'application de manière classique (en double-cliquant sur l'icône) :

- Allez dans le dossier `dist`.
- Faites un clic droit sur `job_gestion.app`, puis "Ouvrir" pour contourner les restrictions de macOS.

## Utilisation

1. **Ajouter une candidature** :

   - Cliquez sur le bouton "Nouvelle candidature".
   - Remplissez les champs requis : nom de l'entreprise, titre du poste, chemin vers la lettre de motivation et le screenshot, statut, et commentaire.
   - Cliquez sur "Sauvegarder".

2. **Modifier une candidature** :

   - Depuis l'écran principal, cliquez sur "Modifier / Voir" pour une candidature.
   - Modifiez les informations et cliquez sur "Sauvegarder".

3. **Supprimer une candidature** :
   - Depuis l'écran principal, cliquez sur "Modifier / Voir" pour une candidature.
   - Cliquez sur "Supprimer" et confirmez la suppression.

## Déploiement via GitHub

Pour rendre cette application téléchargeable via GitHub :

1. **Compressez l'application** :

   - Accédez au répertoire `dist/` qui contient `job_gestion.app`.
   - Compressez-la en un fichier `.zip` :
     ```bash
     cd dist
     zip -r job_gestion.zip job_gestion.app
     ```

2. **Publiez sur GitHub** :

   - Créez une nouvelle release sur la page GitHub du projet.
   - Ajoutez le fichier `job_gestion.zip` en tant qu'asset de la release.

3. **Instructions d'installation** :

   - Dans le fichier `README.md` sur GitHub, ajoutez des instructions pour expliquer comment télécharger et installer l'application :

     ```markdown
     ## Installation

     1. Rendez-vous sur la [page des releases](https://github.com/SC138/JobGestion/releases).
     2. Téléchargez le fichier `job_gestion.zip`.
     3. Décompressez le fichier et déplacez `job_gestion.app` dans votre dossier `Applications`.
     4. Faites un clic droit sur l'application, puis "Ouvrir" pour l'exécuter.
     ```

## Notes importantes

- **Système de fichiers en lecture seule** : L'application sauvegarde les données dans le répertoire utilisateur. Cela assure que les permissions sont respectées et que l'application peut lire/écrire sans problème.
- **Compatibilité macOS** : Cette version est développée pour macOS. Pour Windows, une adaptation ultérieure sera nécessaire.

## Prochaines étapes

- **Adaptation pour Windows** : étendre la compatibilité à Windows en générant un `.exe` avec PyInstaller.
- **Nouvelles fonctionnalités** : Ajouter plus de champs ou des options avancées pour la gestion des candidatures.

Merci d'utiliser **JobGestion** !

## Auteur

- **Thomas Chevron** - [LinkedIn](https://www.linkedin.com/in/thomas-chevron/)

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
