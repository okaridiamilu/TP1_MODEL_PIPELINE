import re
from copy import deepcopy

#deepcopy fait des copies d'objet, pratique pour donc copier la liste d'étudiants pour en faire une nouvelle pour effectuer des tests dessus, sans toucher à la liste originale  # noqa: E501
# flask va servir a faire l'api rest. client -> flask -> fonctions -> gather datas -> flask -> client.  # noqa: E501
from flask import Flask, jsonify, request

#jsonify transforme un dictionnaire python en json pour le renvoyer au client, request va permettre de récupérer les données envoyées par le client.  # noqa: E501

INITIAL_STUDENTS = [
    {
        "id": 1,
        "firstName": "Alice",
        "lastName": "Martin",
        "email": "alice.martin@example.com",
        "grade": 16.5,
        "field": "informatique",
    },
    {
        "id": 2,
        "firstName": "Benoit",
        "lastName": "Durand",
        "email": "benoit.durand@example.com",
        "grade": 14.0,
        "field": "mathematiques",
    },
    {
        "id": 3,
        "firstName": "Chloe",
        "lastName": "Bernard",
        "email": "chloe.bernard@example.com",
        "grade": 18.0,
        "field": "physique",
    },
    {
        "id": 4,
        "firstName": "David",
        "lastName": "Petit",
        "email": "david.petit@example.com",
        "grade": 12.5,
        "field": "chimie",
    },
    {
        "id": 5,
        "firstName": "Emma",
        "lastName": "Robert",
        "email": "emma.robert@example.com",
        "grade": 15.0,
        "field": "informatique",
    },
]
# Fait donc une copie de la liste initiale d'étudiants pour pouvoir la modifier sans toucher à l'originale.  # noqa: E501
students = deepcopy(INITIAL_STUDENTS)
ALLOWED_FIELDS = {"informatique", "mathematiques", "physique", "chimie"}
REQUIRED_FIELDS = {"firstName", "lastName", "email", "grade", "field"}

# Reinitialise la liste des étudiants à son état initial
def reset_students() -> None:
    students.clear()
    students.extend(deepcopy(INITIAL_STUDENTS))

# Vérifie l'intégrité des données d'un étudiant, en s'assurant que les champs requis sont présents et valides.  # noqa: E501

# Dans les arguments, Data c'est un JSON envoyé en requete POST donc dedans on va retrouver des datas étudiants sous la forme de dictionaire (en gros, c'est le bout de dictionnaire qui va etre proposé si on veut faire une action crud pour interragire avec la bdd, donc on regarde bien qu'il est bien dans les normes.)  # noqa: E501
# ,data reçois tout type d'objet, mais on vérifie juste apres que c'est un dictionnaire, qui en réalité est un JSON, mais on dit que c'est un dict  # noqa: E501
# , current_id c'est l'id de l'étudiant qu'on est en train de modifier, si on est en train de créer un nouvel étudiant, on met None, sinon on met l'id de l'étudiant qu'on est en train de modifier  # noqa: E501
# , la fonction retourne soit une chaine de caractère qui est l'erreur, soit None si tout est ok  # noqa: E501
# , si y avait toujours un doute le "|" c'est un ou.

def validate_student_data(data: object, current_id: int | None = None) -> str | None:
    if not isinstance(data, dict):
        return "Le corps de la requete doit etre un objet JSON"

    # Vue que tout le REQUIRED_FIELDS est une liste de champs identique aux clé du dictionnaire, faire une soustraction va donc faire une liste de tous les champs qui sont pas présents.  # noqa: E501
    missing_fields = REQUIRED_FIELDS - data.keys()
    if missing_fields:
        return f"Champs obligatoires manquants: {', '.join(sorted(missing_fields))}"

    # On vérifie que les champs sont bien du bon type et respectent les contraintes de validation (min 2 char).  # noqa: E501
    if not isinstance(data["firstName"], str) or len(data["firstName"].strip()) < 2:
        return "firstName doit contenir au moins 2 caracteres"
    if not isinstance(data["lastName"], str) or len(data["lastName"].strip()) < 2:
        return "lastName doit contenir au moins 2 caracteres"
    if not isinstance(data["email"], str) or not re.fullmatch(
        # "---------@----.----" (c'est un regex)
        r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]
    ):
        return "email doit avoir un format valide"
    if any(
        student["email"].lower() == data["email"].lower()
        and student["id"] != current_id
        for student in students
    ):
        return "email existe deja"
    # on les bool car on veut pas que le grade soit un booléen, car en python, True et False sont des sous-classes de int, donc isinstance(True, int) retourne True.  # noqa: E501
    if isinstance(data["grade"], bool) or not isinstance(data["grade"], (int, float)):
        return "grade doit etre un nombre entre 0 et 20"
    if not 0 <= data["grade"] <= 20:
        return "grade doit etre un nombre entre 0 et 20"
    if data["field"] not in ALLOWED_FIELDS:
        return "field doit etre une filiere autorisee"

    return None


#transforme l'id qui est un string en int. renvoie une erreur sinon.
def parse_student_id(raw_id: str) -> tuple[int | None, tuple[dict, int] | None]:
    try:
        return int(raw_id), None
    except ValueError:
        return None, ({"error": "L'identifiant doit etre un nombre"}, 400)




def create_app() -> Flask:
    app = Flask(__name__)

    # a la racine de l'api, on retourne un message de bienvenue
    @app.get("/")
    def home() -> dict[str, str]:
        return {"message": "Bienvenue dans le projet Flask"}

    # a la page /health, on retourne un status ok pour dire que l'api est en vie
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # a la page /students, on retourne la liste des étudiants
    @app.get("/students")
    def get_students():
        return jsonify(students), 200

    @app.get("/students/stats")
    def get_stats():
        total_students = len(students)
        average_grade = round(
            sum(student["grade"] for student in students) / total_students, 2
        )
        students_by_field = {
            field: sum(student["field"] == field for student in students)
            for field in sorted(ALLOWED_FIELDS)
        }
        best_student = max(students, key=lambda student: student["grade"])
        return {
            "totalStudents": total_students,
            "averageGrade": average_grade,
            "studentsByField": students_by_field,
            "bestStudent": best_student,
        }, 200

    @app.get("/students/search")
    def search_students():
        query = request.args.get("q", "").strip().lower()
        if not query:
            return {"error": "Le parametre q est obligatoire"}, 400
        matches = [
            student
            for student in students
            if query in student["firstName"].lower()
            or query in student["lastName"].lower()
        ]
        return jsonify(matches), 200

    @app.get("/students/<student_id>")
    def get_student(student_id: str):
        parsed_id, error = parse_student_id(student_id)
        if error:
            return error
        student = next((item for item in students if item["id"] == parsed_id), None)
        if student is None:
            return {"error": "Etudiant introuvable"}, 404
        return student, 200

    @app.post("/students")
    def create_student():
        data = request.get_json(silent=True)
        validation_error = validate_student_data(data)
        if validation_error:
            status_code = 409 if validation_error == "email existe deja" else 400
            return {"error": validation_error}, status_code

        new_student = {key: data[key] for key in REQUIRED_FIELDS}
        new_student["id"] = max((student["id"] for student in students), default=0) + 1
        students.append(new_student)
        return new_student, 201

    @app.put("/students/<student_id>")
    def update_student(student_id: str):
        parsed_id, error = parse_student_id(student_id)
        if error:
            return error
        student = next((item for item in students if item["id"] == parsed_id), None)
        if student is None:
            return {"error": "Etudiant introuvable"}, 404

        data = request.get_json(silent=True)
        validation_error = validate_student_data(data, current_id=parsed_id)
        if validation_error:
            status_code = 409 if validation_error == "email existe deja" else 400
            return {"error": validation_error}, status_code
        student.update({key: data[key] for key in REQUIRED_FIELDS})
        return student, 200

    @app.delete("/students/<student_id>")
    def delete_student(student_id: str):
        parsed_id, error = parse_student_id(student_id)
        if error:
            return error
        student = next((item for item in students if item["id"] == parsed_id), None)
        if student is None:
            return {"error": "Etudiant introuvable"}, 404
        students.remove(student)
        return {"message": "Etudiant supprime"}, 200

    return app


app = create_app()