"""Tests for Skill service response format"""
import pytest
from unittest.mock import Mock
from services.skill_service import SkillService
from db.repository.skills import SkillRepository


class TestSkillServiceResponseFormat:
    """Test that search_skills returns consistent response format"""

    def test_search_skills_returns_correct_field_names(self):
        """search_skills should return skill_id, skill_name, image_url"""
        skill_repo = Mock(spec=SkillRepository)
        service = SkillService(skill_repo)

        # Mock skill objects
        mock_skill = Mock()
        mock_skill.id = 1
        mock_skill.name = "Python"
        mock_skill.image_url = "https://example.com/python.png"

        skill_repo.get_all_flat = Mock(return_value=[mock_skill])

        result = service.search_skills("python")

        # Verify response is list of dicts
        assert len(result) > 0
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

        # Verify field names
        assert "skill_id" in result[0]
        assert "skill_name" in result[0]
        assert "image_url" in result[0]

    def test_search_skills_maps_model_fields_correctly(self):
        """search_skills should map skill model id→skill_id, name→skill_name"""
        skill_repo = Mock(spec=SkillRepository)
        service = SkillService(skill_repo)

        mock_skill = Mock()
        mock_skill.id = 5
        mock_skill.name = "React"
        mock_skill.image_url = "https://example.com/react.png"

        skill_repo.get_all_flat = Mock(return_value=[mock_skill])

        result = service.search_skills("react")

        assert result[0]["skill_id"] == 5
        assert result[0]["skill_name"] == "React"
        assert result[0]["image_url"] == "https://example.com/react.png"

    def test_search_skills_handles_null_image_url(self):
        """search_skills should return empty string when image_url is None"""
        skill_repo = Mock(spec=SkillRepository)
        service = SkillService(skill_repo)

        mock_skill = Mock()
        mock_skill.id = 1
        mock_skill.name = "JavaScript"
        mock_skill.image_url = None

        skill_repo.get_all_flat = Mock(return_value=[mock_skill])

        result = service.search_skills("javascript")

        # Should have empty string, not None
        assert result[0]["image_url"] == ""

    def test_search_skills_fuzzy_matching(self):
        """search_skills should perform fuzzy matching with threshold"""
        from unittest.mock import MagicMock

        skill_repo = Mock(spec=SkillRepository)
        service = SkillService(skill_repo)

        # Create Mock skills - use actual strings for name since fuzzy matching needs real strings
        skill1 = Mock()
        skill1.id = 1
        skill1.name = "Python"
        skill1.image_url = "url1"

        skill2 = Mock()
        skill2.id = 2
        skill2.name = "JavaScript"
        skill2.image_url = "url2"

        skill3 = Mock()
        skill3.id = 3
        skill3.name = "TypeScript"
        skill3.image_url = "url3"

        skills = [skill1, skill2, skill3]

        skill_repo.get_all_flat = Mock(return_value=skills)

        # Search for "java" should match both Java and JavaScript
        result = service.search_skills("java")

        # Should find JavaScript at minimum
        assert len(result) > 0
        # Should contain JavaScript
        found_js = any(s["skill_name"] == "JavaScript" for s in result)
        assert found_js
