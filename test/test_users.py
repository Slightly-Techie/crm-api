from api.api_models import user
import pytest
from jose import jwt
from core.config import settings



def test_sign_up(client):
    res=client.post(
      "/api/v1/users/register/" , json={"username": "slightlytechie1","first_name": "Slightly", "last_name": "Techie", "email": "slightlytechie@gmail.com", "password": "food", "password_confirmation": "food", "years_of_experience": 5, "bio": "I am almost a techie", "phone_number": "233567895423", "is_active": True}
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