# invoice-calc

Compute and render simple invoices with line items, one VAT rate and an optional discount.
Money is `decimal.Decimal` throughout; amounts are rounded to the cent.

```python
from decimal import Decimal
from invoice import Invoice, LineItem, render_text

inv = Invoice(
    number="2026-001",
    customer="Acme GmbH",
    items=[LineItem("Consulting day", 2, Decimal("950.00"))],
    discount_pct=Decimal("5"),
)
print(render_text(inv))
```

Run the tests with `python -m pytest`.
