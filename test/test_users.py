from api.api_models import user
from fastapi import HTTPException
import pytest
from jose import jwt
from core.config import settings



def test_sign_up(client):
    res=client.post(
      "/api/v1/users/register/" , json={"first_name": "Slightly", "last_name": "Techie", "email": "slightlytechie@gmail.com", "password": "food", "password_confirmation": "food", "years_of_experience": 5, "bio": "I am almost a techie", "phone_number": "233567895423", "is_active": True}
    )
    new_user = user.UserResponse(**res.json())

    assert new_user.email == "slightlytechie@gmail.com"
    assert res.status_code == 201


def test_log_in(client,test_user):
    res=client.post(
      "/api/v1/users/login" , data={"username": test_user.get("email"), "password": test_user.get("password")}
    )
    res_login = user.Token(**res.json())
    payload = jwt.decode(res_login.token, settings.SECRET, algorithms=settings.ALGORITHM)
    sub = payload.get('sub')

    assert res.status_code == 200
    assert sub == str(test_user.get("id"))
    assert res_login.token_type == "Bearer"


@pytest.mark.parametrize("email, password, status_code",[
  ("incorrectemail@gmail.com", "food", 400),
  ("slightlytechie@gmail.com", "incorrectpassword", 400),
  ("incorrectemail@gmail.com", "incorrectpassword", 400),
  (None, "food", 422),
  ("slightlytechie@gmail.com", None, 422),
])
def test_incorrect_log_in(client, email, password, status_code):
    res = client.post("/api/v1/users/login", data={"username": email, "password": password})
    assert res.status_code == status_code
    
    
def test_get_user_list(client, login_user):
    # Get logged in user token
    # This uses fixture test_user as default logged in user
    user_cred = login_user()

    # Construct header
    header = {"Authorization": f"Bearer {user_cred.get('token')}"}
    
    get_request = client.get("/api/v1/users", headers=header)
    
    # topology of the final response unknown yet.
    # uncertain if status_code will be included with the list of users
    # appended at the beginning of the function.
    # json format unknown at the moment to make final assertions.
    # but i believe the following will do.
    assert get_request.status_code == 200
    assert len(get_request.json()) == 1
    
    