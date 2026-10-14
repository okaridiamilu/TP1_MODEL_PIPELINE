from app import create_app, reset_students

VALID_STUDENT = {
    "firstName": "Farid",
    "lastName": "Simon",
    "email": "farid.simon@example.com",
    "grade": 13.5,
    "field": "physique",
}

# La c'est full test d'égalité, dans un assert qui laisse passer que si c'est true, donc on fait un check sur tout ce qu'on veut vérifier avec les ressortis d'états attendue, si un seule est pas bon, le assert le verra et va échouer, donc on peut faire un test sur tout ce qu'on veut vérifier, et si un seul est pas bon, le assert le verra et va échouer. Donc c'est un test d'égalité, on compare les deux objets, et si ils sont pas égaux, le test échoue.  # noqa: E501
# C'est nos tests unitaires

def setup_function() -> None:
    reset_students()


def test_home_returns_a_welcome_message() -> None:
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json == {"message": "Bienvenue dans le projet Flask"}


def test_health_returns_ok() -> None:
    client = create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_get_students_returns_five_initial_students() -> None:
    client = create_app().test_client()

    response = client.get("/students")

    assert response.status_code == 200
    assert len(response.json) == 5
    assert response.json[0]["firstName"] == "Alice"


def test_reset_students_restores_initial_data() -> None:
    client = create_app().test_client()
    client.delete("/students/1")

    reset_students()
    response = client.get("/students")

    assert len(response.json) == 5


def test_get_student_by_id_returns_matching_student() -> None:
    response = create_app().test_client().get("/students/1")

    assert response.status_code == 200
    assert response.json["email"] == "alice.martin@example.com"


def test_get_student_with_unknown_id_returns_not_found() -> None:
    response = create_app().test_client().get("/students/999")

    assert response.status_code == 404


def test_get_student_with_invalid_id_returns_bad_request() -> None:
    response = create_app().test_client().get("/students/abc")

    assert response.status_code == 400


def test_post_student_with_valid_data_creates_student() -> None:
    response = create_app().test_client().post("/students", json=VALID_STUDENT)

    assert response.status_code == 201
    assert response.json["id"] == 6
    assert response.json["firstName"] == "Farid"


def test_post_student_without_required_field_returns_bad_request() -> None:
    incomplete_student = {
        key: value for key, value in VALID_STUDENT.items() if key != "email"
    }

    response = create_app().test_client().post("/students", json=incomplete_student)

    assert response.status_code == 400


def test_post_student_with_invalid_grade_returns_bad_request() -> None:
    invalid_student = {**VALID_STUDENT, "grade": 25}

    response = create_app().test_client().post("/students", json=invalid_student)

    assert response.status_code == 400


def test_post_student_with_existing_email_returns_conflict() -> None:
    duplicate_student = {**VALID_STUDENT, "email": "alice.martin@example.com"}

    response = create_app().test_client().post("/students", json=duplicate_student)

    assert response.status_code == 409


def test_put_student_with_valid_data_updates_student() -> None:
    updated_student = {**VALID_STUDENT, "email": "alice.updated@example.com"}

    response = create_app().test_client().put("/students/1", json=updated_student)

    assert response.status_code == 200
    assert response.json["lastName"] == "Simon"


def test_put_student_with_unknown_id_returns_not_found() -> None:
    response = create_app().test_client().put("/students/999", json=VALID_STUDENT)

    assert response.status_code == 404


def test_delete_student_with_valid_id_returns_confirmation() -> None:
    response = create_app().test_client().delete("/students/1")

    assert response.status_code == 200
    assert response.json == {"message": "Etudiant supprime"}


def test_delete_student_with_unknown_id_returns_not_found() -> None:
    response = create_app().test_client().delete("/students/999")

    assert response.status_code == 404


def test_stats_returns_expected_summary() -> None:
    response = create_app().test_client().get("/students/stats")

    assert response.status_code == 200
    assert response.json["totalStudents"] == 5
    assert response.json["averageGrade"] == 15.2
    assert response.json["bestStudent"]["firstName"] == "Chloe"


def test_search_returns_case_insensitive_matches() -> None:
    response = create_app().test_client().get("/students/search?q=alice")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["lastName"] == "Martin"


def test_search_without_query_returns_bad_request() -> None:
    response = create_app().test_client().get("/students/search")

    assert response.status_code == 400