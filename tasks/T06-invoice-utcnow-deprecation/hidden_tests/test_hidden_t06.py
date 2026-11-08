import warnings
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from invoice import Invoice, LineItem, render_text


def make():
    return Invoice(number="H-6", customer="Acme GmbH", items=[LineItem("Day", 1, Decimal("900"))])


def test_no_deprecation_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        inv = make()
        render_text(inv)


def test_default_is_aware_utc_now():
    inv = make()
    assert inv.issued_at.tzinfo is not None
    assert inv.issued_at.utcoffset() == timedelta(0)
    assert abs(datetime.now(UTC) - inv.issued_at) < timedelta(minutes=1)


def test_due_date_follows_issue_date():
    inv = make()
    assert inv.due_date == (inv.issued_at + timedelta(days=30)).date()
