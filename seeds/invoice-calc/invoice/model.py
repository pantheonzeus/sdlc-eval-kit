"""Invoice data model."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal

from invoice.money import to_money


@dataclass(frozen=True)
class LineItem:
    description: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        object.__setattr__(self, "unit_price", to_money(self.unit_price))


@dataclass
class Invoice:
    number: str
    customer: str
    items: list[LineItem]
    vat_rate: Decimal = Decimal("19")
    discount_pct: Decimal = Decimal("0")
    payment_terms_days: int = 30
    issued_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("an invoice needs at least one line item")
        if not Decimal("0") <= self.discount_pct <= Decimal("100"):
            raise ValueError("discount_pct must be between 0 and 100")

    @property
    def due_date(self) -> date:
        return (self.issued_at + timedelta(days=self.payment_terms_days)).date()
