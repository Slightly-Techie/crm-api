from fastapi import HTTPException, status

from db.repository.endpoints import EndpointRepository


class EndpointService:
    def __init__(self, endpoint_repo: EndpointRepository):
        self.endpoint_repo = endpoint_repo

    def is_signup_open(self) -> None:
        """Raise 403 if the signup endpoint is disabled. Auto-creates with status=True if missing."""
        obj = self.endpoint_repo.get_by_name("signup")
        if obj is None:
            self.endpoint_repo.create("signup", status=True)
            return
        if not obj.status:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Signup is closed")

    def add_endpoint(self, endpoint_name: str) -> None:
        if self.endpoint_repo.get_by_name(endpoint_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Endpoint already exists"
            )
        self.endpoint_repo.create(endpoint_name, status=True)

    def toggle_endpoint(self, endpoint_name: str) -> None:
        obj = self.endpoint_repo.get_by_name(endpoint_name)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Endpoint {endpoint_name} not found"
            )
        self.endpoint_repo.toggle(obj)
