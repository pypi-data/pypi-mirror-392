from typing import Tuple
from uuid import UUID
from maleo.enums.organization import OrganizationRole


CompositeIdentifierType = Tuple[int, int, OrganizationRole]
IdentifierValueType = int | UUID | CompositeIdentifierType
