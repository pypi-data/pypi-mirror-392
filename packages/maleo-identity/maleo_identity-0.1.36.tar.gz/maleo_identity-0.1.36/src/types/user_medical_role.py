from typing import Tuple
from uuid import UUID
from maleo.enums.medical import MedicalRole


CompositeIdentifierType = Tuple[int, int, MedicalRole]
IdentifierValueType = int | UUID | CompositeIdentifierType
