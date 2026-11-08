"""Plain-text rendering of an invoice."""

from invoice.calc import discount_amount, line_net, subtotal, total, vat_amount
from invoice.model import Invoice
from invoice.money import format_eur

WIDTH = 60


def render_text(invoice: Invoice) -> str:
    """Render the invoice as fixed-width text."""
    lines = [
        f"INVOICE {invoice.number}",
        f"Customer: {invoice.customer}",
        f"Issued: {invoice.issued_at:%Y-%m-%d}   Due: {invoice.due_date:%Y-%m-%d}",
        "-" * WIDTH,
    ]
    for item in invoice.items:
        left = f"{item.quantity} x {item.description}"
        lines.append(_row(left, format_eur(line_net(item))))
    lines.append("-" * WIDTH)
    lines.append(_row("Subtotal", format_eur(subtotal(invoice))))
    if invoice.discount_pct:
        lines.append(_row(f"Discount {invoice.discount_pct}%", format_eur(-discount_amount(invoice))))
    lines.append(_row(f"VAT {invoice.vat_rate}%", format_eur(vat_amount(invoice))))
    lines.append(_row("Total", format_eur(total(invoice))))
    return "\n".join(lines) + "\n"


def _row(left: str, right: str) -> str:
    return f"{left:<{WIDTH - len(right)}}{right}"
