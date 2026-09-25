from dataclasses import dataclass
from decimal import Decimal


class Dec4(Decimal):
    pass


@dataclass
class AddItemData:
    old_barcode: str = ""
    barcode: str = ""
    name: str = ""
    price: Decimal = Decimal("0")
    taxable: int = 0
    category: str = ""
    subcategory: str = ""
    vendor: str = ""
    quantity: Dec4 = Dec4("0")
