import sqlite3
from dataclasses import dataclass
from datetime import datetime
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
    reconciled: bool = False
    date_last_reconciled: datetime = datetime.now()


@dataclass
class Receipt:
    sale_info: SaleInfo
    sale_items_info: list[SaleItemsInfo]


@dataclass
class SaleInfo:
    sale_id: int
    non_tax: Decimal
    pre_tax: Decimal
    tax: Decimal
    total: Decimal


@dataclass
class SaleItemsInfo:
    price_at_sale: Decimal
    quantity: Dec4
    item_name: str
    item_taxable: int
    item_id: int
