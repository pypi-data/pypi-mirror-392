from typing import Tuple
from uuid import UUID
from maleo.enums.medical import MedicalRole


BasicIdentifierType = int | UUID
CompositeIdentifierType = Tuple[int, int, MedicalRole]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
