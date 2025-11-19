from typing import Protocol, List, Optional
from baltra_sdk.domain.models.screening_flow import MessageTemplate


class MessageTemplateRepository(Protocol):
    """Base interface for interacting with message templates."""

    def create(self, template: MessageTemplate) -> MessageTemplate:
        """Creates a new template and saves it to the database."""
        ...

    def bulk_create(self, templates: List[MessageTemplate]) -> List[MessageTemplate]:
        """Creates multiple templates at once."""
        ...

    def get(self, template_id: int) -> Optional[MessageTemplate]:
        """Gets a template by its ID."""
        ...

    def find_by_company(self, company_id: int) -> List[MessageTemplate]:
        """Returns all templates associated with a company."""
        ...

    def find_by_keyword(self, company_id: int, keyword: str) -> Optional[MessageTemplate]:
        """Searches for a specific template by keyword within a company."""
        ...

    def delete(self, template_id: int) -> None:
        """Deletes a template by ID."""
        ...
