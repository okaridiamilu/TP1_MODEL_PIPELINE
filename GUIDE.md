# Initialisation du projet Python

Ce TP utilise Flask comme framework web, pytest pour les tests et Ruff comme
linter. Le fichier `pyproject.toml` centralise les dependances et la
configuration des outils.

## 1. Creer un environnement virtuel

Depuis ce dossier :

### (pour moi de moi a moi) Le scrypt va permettre donc de faire un environnement dans le fichier. venv c'est donc le truc python pour faire un V(irtual)ENV(ironment)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

L'environnement virtuel isole les dependances du TP de celles de Python
installees sur la machine.

## 2. Installer les dependances


```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

`-e` installe le projet en mode editable. `[dev]` demande aussi les outils
utiles au developpement, ici pytest et Ruff. Flask est une dependance normale
de l'application.

## 3. Demarrer le serveur

```powershell
python -m flask --app app run --debug
```

Ouvrir ensuite `http://127.0.0.1:5000/` ou `/health`. `--debug` recharge le
serveur quand le code change; il est reserve au developpement local.

## 4. Lancer les tests

### (pour moi de moi a moi) C'est notre liste de tests unitaires.

```powershell
python -m pytest
```

Les tests de `tests/test_app.py` utilisent le client de test Flask, donc ils
ne necessitent pas de demarrer un serveur reel.

## 5. Lancer le linter

### (pour moi de moi a moi) En gris un linter (ruff) dans notre cas va juste clean notre code, trucs inutiles ou mal fait. ça inspecte et ça fait des signalements. C'est bien comme étape de vérif initiale avant de d'avancer plus profondément dans les phases de testes.

```powershell
ruff check .
```

Ruff verifie les erreurs de style et certains problemes Python. Les regles
activees (`E`, `F`, `I`) sont definies et expliqué dans `pyproject.toml`.



## 6. Comprendre l'application avec une image

Imagine une bibliotheque universitaire :

- `students` est le carnet pose sur le comptoir. Il contient les etudiants en
	memoire et disparait quand l'application redemarre.
- `INITIAL_STUDENTS` est la photocopie du carnet de depart.
- `reset_students()` remplace le carnet actuel par cette photocopie. Les tests
	l'utilisent pour repartir d'une situation connue.
- Flask est le bibliothecaire : chaque URL est un guichet specialise.
- Une requete HTTP est une demande d'un visiteur; la reponse JSON est la fiche
	que le bibliothecaire lui remet, avec un code qui explique le resultat.

Par exemple, `GET /students/1` signifie : « donne-moi la fiche de l'etudiant
1 ». `POST /students` signifie : « ajoute cette nouvelle fiche ». Le serveur
ne renvoie pas seulement des donnees : `200` signifie succes, `201` creation,
`400` demande incorrecte, `404` fiche absente et `409` conflit, par exemple un
email deja utilise.

La fonction `create_app()` construit l'application sans lancer de serveur.
C'est comme fabriquer le guichet dans une salle de test. Pytest peut alors
utiliser le client Flask pour envoyer des requetes directement, sans ouvrir un
port sur l'ordinateur.

## 7. Role des fichiers

- `app.py` contient l'application Flask et ses routes.
- `tests/test_app.py` verifie le comportement attendu.
- `pyproject.toml` decrit le projet, ses dependances et ses outils.
- `.gitignore` exclut les fichiers locaux ou generes de Git.

## 8. Integration continue avec GitHub Actions

Le fichier `.github/workflows/ci.yml` automatise les controles sur GitHub :

1. `actions/checkout` recupere le code.
2. `actions/setup-python` installe Python 3.12 puis 3.14, grace a la matrice.
3. `pip install -e ".[dev]"` installe l'application et les outils.
4. `ruff check .` verifie le style.
5. `python -m pytest` lance les tests.

Le workflow s'execute automatiquement lors d'un push ou d'une pull request.
Si un test ou le linter echoue, GitHub Actions marque la verification en echec.

## 9. Le TP explique comme un parcours

Le sujet demande de construire une petite maison logicielle, puis de placer un
controleur automatique devant sa porte :

1. **Fondations** : `pyproject.toml` installe Flask, pytest et Ruff.
2. **Carnet** : `INITIAL_STUDENTS` fournit cinq fiches et `reset_students()`
	garantit des tests independants.
3. **Guichets** : `app.py` expose les sept endpoints demandes. Les routes
	`/students/stats` et `/students/search` sont placees avant
	`/students/<student_id>` pour ne pas etre prises pour des identifiants.
4. **Reglement interieur** : `validate_student_data()` controle les champs,
	les noms, l'email, la note, la filiere et l'unicite.
5. **Simulations** : `tests/test_app.py` contient 18 tests, couvrant les
	succes et les erreurs des operations GET, POST, PUT, DELETE, stats et
	recherche.
6. **Inspecteur** : Ruff bloque les erreurs de style avant la suite de tests.
7. **Gardien automatique** : GitHub Actions rejoue linting et tests sur Python
	3.12 et 3.14 a chaque push ou pull request.

Les attentes du TP sont donc reliees a des preuves : les endpoints sont
verifies par les tests, les validations produisent les codes HTTP attendus,
Ruff doit terminer sans erreur et la matrice CI verifie deux environnements.
Pour le rendu final, il reste a pousser le depot GitHub, utiliser des commits
Conventional Commits et capturer un passage rouge puis un passage vert du
pipeline.
