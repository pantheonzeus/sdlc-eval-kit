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


def vat_breakdown(invoice: Invoice) -> dict[Decimal, tuple[Decimal, Decimal]]:
    """Per VAT rate, highest first: (net after discount, VAT)."""
    nets: dict[Decimal, Decimal] = {}
    for item in invoice.items:
        rate = invoice.vat_rate if item.vat_rate is None else item.vat_rate
        nets[rate] = nets.get(rate, Decimal("0")) + line_net(item)
    keep = 1 - invoice.discount_pct / HUNDRED
    breakdown = {}
    for rate in sorted(nets, reverse=True):
        net = round_money(nets[rate] * keep)
        breakdown[rate] = (net, round_money(net * rate / HUNDRED))
    return breakdown


def vat_amount(invoice: Invoice) -> Decimal:
    """VAT summed over the rates in the breakdown."""
    return sum((vat for _, vat in vat_breakdown(invoice).values()), Decimal("0"))


def total(invoice: Invoice) -> Decimal:
    """Amount payable: discounted subtotal plus VAT."""
    return subtotal(invoice) - discount_amount(invoice) + vat_amount(invoice)
