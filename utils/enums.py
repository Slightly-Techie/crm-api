from enum import Enum

class UserStatus(str, Enum):
    
    TO_CONTACT = "TO CONTACT"
    IN_REVIEW = "IN REVIEW"
    INTERVIEWED = "INTERVIEWED"
    ACCEPTED = "ACCEPTED"
    NO_SHOW = "NO SHOW"
    REJECTED = "REJECTED"
    TO_BE_ONBOARDED = "TO BE ONBOARDED"
    CONTACTED = "CONTACTED"

class ProjectType(str, Enum):
    
    COMMUNITY = "COMMUNITY"
    PAID = "PAID"
    
class ProjectPriority(str, Enum):
    
    LOW_PRIORITY = "LOW PRIORITY"
    MEDIUM_PRIORITY = "MEDIUM PRIORITY"
    HIGH_PRIORITY = "HIGH PRIORITY"
    
class ProjectTeam(str, Enum):
    TEAM_LEAD = "TEAM LEAD"
    FRONTEND = "FRONTEND"
    BACKEND = "BACKEND"
    DEVOPS = "DEVOPS"
    DESIGNER = "DESIGNER"
    MOBILE = "MOBILE"
    FULL_STACK = "FULL STACK"
    