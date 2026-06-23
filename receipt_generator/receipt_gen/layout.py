"""
Builds a structured, randomised receipt as a plain Python dict. This dict
IS the ground-truth JSON target paired with the rendered image.
"""

import random
import datetime

from . import data


def _round2(x):
    return round(x + 1e-9, 2)


def build_receipt(store_key=None, min_items=4, max_items=22, seed=None):
    if seed is not None:
        random.seed(seed)

    store_key = store_key or random.choice(list(data.STORE_PROFILES.keys()))
    profile = data.STORE_PROFILES[store_key]

    branch_info = random.choice(profile["branches"])
    branch = branch_info["name"]
    town = branch_info["town"]
    postcode = branch_info["postcode"]
    street_no = random.randint(1, 220)
    street = random.choice(data.STREET_NAMES)

    now = datetime.datetime.now() - datetime.timedelta(
        days=random.randint(0, 540),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    n_items = random.randint(min_items, max_items)
    chosen = random.choices(data.ITEM_CATALOG, k=n_items)

    items = []
    for name, category, lo, hi in chosen:
        unit_price = _round2(random.uniform(lo, hi))
        # Most items qty 1, occasionally 2-3
        qty = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
        total_price = _round2(unit_price * qty)
        vat_code = data.VAT_CODES.get(category, "A")
        items.append({
            "name": name,
            "category": category,
            "quantity": qty,
            "unit_price": unit_price,
            "total_price": total_price,
            "vat_code": vat_code,
        })

    subtotal = _round2(sum(i["total_price"] for i in items))

    # VAT breakdown
    vat_breakdown = []
    for code in sorted(set(i["vat_code"] for i in items)):
        net = _round2(sum(i["total_price"] for i in items if i["vat_code"] == code))
        rate = data.VAT_RATES[code]
        # UK receipts show VAT-inclusive line prices; back out the VAT amount
        vat_amount = _round2(net - net / (1 + rate)) if rate > 0 else 0.0
        vat_breakdown.append({
            "code": code,
            "label": data.VAT_LABELS[code],
            "net_amount": _round2(net - vat_amount),
            "vat_amount": vat_amount,
            "gross_amount": net,
        })

    total = subtotal

    payment_method = random.choices(["CARD", "CASH"], weights=[80, 20])[0]
    payment = {"method": payment_method}
    if payment_method == "CARD":
        payment["card_type"] = random.choice(data.CARD_TYPES)
        payment["card_last4"] = data.random_card_last4()
        payment["amount_authorised"] = total
    else:
        tendered = _round2(total + random.choice([0, 0.5, 1, 2, 5, 10]))
        tendered = max(tendered, total)
        payment["amount_tendered"] = tendered
        payment["change"] = _round2(tendered - total)

    receipt = {
        "store": {
            "name": profile["name"],
            "legal_name": profile["legal_name"],
            "branch": branch,
            "address": f"{street_no} {street}, {town}, {postcode}",
            "phone": data.random_phone(),
        },
        "transaction": {
            "date": now.strftime("%d/%m/%Y"),
            "time": now.strftime("%H:%M"),
            "receipt_number": data.random_receipt_number(),
            "till_number": str(random.randint(1, 24)).zfill(2),
            "cashier": random.choice(data.CASHIER_NAMES),
        },
        "items": items,
        "totals": {
            "item_count": sum(i["quantity"] for i in items),
            "subtotal": subtotal,
            "vat_breakdown": vat_breakdown,
            "total": total,
        },
        "payment": payment,
        "_style": {
            "store_key": store_key,
            "accent_color": profile["accent_color"],
            "footer_lines": profile["footer_lines"],
        },
    }
    return receipt
