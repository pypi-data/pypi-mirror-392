from typing import Tuple
from uuid import UUID
from maleo.types.integer import OptInt


CompositeIdentifierType = Tuple[int, OptInt]
IdentifierValueType = int | UUID | str | CompositeIdentifierType
