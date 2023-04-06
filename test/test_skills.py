from api.api_models import skills
import pytest


from core.config import settings

#user needs to be authenticated
def test_add_skill(client):
    res=client.post(
      "/api/v1/users/skills/?id=1" , json={"name": "go"}
    )
    #new_skill = skills.SkillBase(**res.json())

    #assert new_skill.name == "go"
    assert res.status_code == 201
    assert res.json() == {"name": "go"}


