from fastapi import status
from db.models.techie_of_the_month import TechieOTM


def test_create_techie_of_the_month(client, test_user, test_user1):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    techieotm_data = {
        "user_id": 2,
        "points": 100,
    }
    response = client.post("/api/v1/users/techieotm/", json=techieotm_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_201_CREATED

    techieotm_response = response.json()
    
    assert techieotm_response["user"]["id"] == 2
    assert techieotm_response["points"] == 100


def test_create_techie_of_the_month_already_posted(client, test_user, test_user1, session):
    db = session
    existing_techieotm = TechieOTM(user_id=1, points=200)
    db.add(existing_techieotm)
    db.commit()
    
    techieotm_data = {
        "user_id": 2,
        "points": 100,
    }

    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    techieotm_data = {
        "user_id": 2,
        "points": 100,
    }
    response = client.post("/api/v1/users/techieotm/", json=techieotm_data, headers={'Authorization': f'Bearer {token}'})


    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Techie of the Month already posted for the current month"


def test_non_admin_create_techie_of_the_month(client, test_user, test_user1):
    login_res = client.post("/api/v1/users/login", data={"username": test_user1["email"], "password": test_user1["password"]})
    token = login_res.json()["token"]
    
    techieotm_data = {
        "user_id": 2,
        "points": 100,
    }
    response = client.post("/api/v1/users/techieotm/", json=techieotm_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_techie_of_the_month_not_exist(client, test_user, test_user1):
    login_res = client.post("/api/v1/users/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = login_res.json()["token"]
    
    techieotm_data = {
        "user_id": 1000,
        "points": 100,
    }
    response = client.post("/api/v1/users/techieotm/", json=techieotm_data, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_latest_techie_of_the_month(client, test_user, session):
    db = session
    latest_techieotm = TechieOTM(user_id=1, points=200)
    db.add(latest_techieotm)
    db.commit()

    response = client.get("/api/v1/users/techieotm/latest")

    assert response.status_code == status.HTTP_200_OK

    techieotm_response = response.json()
    assert techieotm_response["id"] == latest_techieotm.id
    assert techieotm_response["user"]["id"] == latest_techieotm.user_id
    

def test_get_all_techies_of_the_months(client, test_user, session):
    db = session
    techieotms = [
        TechieOTM(user_id=1, points=200)
    ]
    db.add_all(techieotms)
    db.commit()

    response = client.get("/api/v1/users/techieotm/?limit=2&page=1")
    assert response.status_code == status.HTTP_200_OK

    techieotm_response = response.json()
    assert len(techieotm_response["techies"]) == 1
    assert techieotm_response["total"] == 1
    assert techieotm_response["page"] == 1
    assert techieotm_response["size"] == 2
    assert len(techieotm_response["links"]) == 5

    first_techieotm = techieotm_response["techies"][0]
    assert first_techieotm["points"] == 200
 
