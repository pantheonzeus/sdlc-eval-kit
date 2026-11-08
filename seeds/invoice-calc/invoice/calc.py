"""Invoice arithmetic. All results are rounded to the cent."""

from decimal import Decimal

from invoice.model import Invoice, LineItem
from invoice.money import round_money

HUNDRED = Decimal("100")


def line_net(item: LineItem) -> Decimal:
    """Net amount of one line: quantity times unit price."""
    return round_money(item.unit_price * item.quantity)


def subtotal(invoice: Invoice) -> Decimal:
    """Sum of all line nets, before discount."""
    return sum((line_net(item) for item in invoice.items), Decimal("0"))


def discount_amount(invoice: Invoice) -> Decimal:
    """Discount on the subtotal."""
    return round_money(subtotal(invoice) * invoice.discount_pct / HUNDRED)


def vat_amount(invoice: Invoice) -> Decimal:
    """VAT on the discounted subtotal."""
    net = subtotal(invoice) - discount_amount(invoice)
    return round_money(net * invoice.vat_rate / HUNDRED)


def total(invoice: Invoice) -> Decimal:
    """Amount payable: discounted subtotal plus VAT."""
    return subtotal(invoice) - discount_amount(invoice) + vat_amount(invoice)
