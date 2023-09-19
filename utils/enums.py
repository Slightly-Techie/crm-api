from enum import Enum

class UserStatus(str, Enum):
    
    TO_CONTACT = "To contact"
    IN_REVIEW = "In review"
    INTERVIEWED = "Interviewed"
    ACCEPTED = "Accepted"
    NO_SHOW = "No show"
    REJECTED = "Rejected"
    TO_BE_ONBOARDED = "To be onboarded"
    CONTACTED = "Contacted"