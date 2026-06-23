# Synthetic Supermarket Receipt Generator (Mostly Claude generated, I made a few tweaks to make it compactable with Windows)

Generates synthetic UK supermarket-style receipts as **image + JSON pairs**,
for training/evaluating OCR or document-parsing models (the same shape of
data as SROIE / CORD: a receipt image with structured ground truth).

Two store styles are included (`asda`, `aldi`) — these only borrow plain
text/layout conventions (store name as text, typical UK till-receipt
formatting, VAT codes, etc.), not any real logo artwork.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Generate 500 photographed-look receipts (default) into ./dataset
python3 generate_receipts.py --count 500 --out ./dataset

# Crisp/clean digital look instead of photographed
python3 generate_receipts.py --count 200 --out ./dataset_clean --style clean

# Mix of clean and photographed in the same batch
python3 generate_receipts.py --count 200 --out ./dataset_mixed --style random

# Only ASDA-style, or only Aldi-style
python3 generate_receipts.py --count 100 --out ./dataset_asda --store asda

# Reproducible batch (same seed -> same receipts)
python3 generate_receipts.py --count 100 --out ./dataset --seed 42
```

Each run produces, per receipt:

```
dataset/images/receipt_00001.jpg   <- the image (the model input)
dataset/json/receipt_00001.json  <- the ground truth (the model target)
```

## What's in the JSON

```json
{
  "store": {"name": "ASDA", "legal_name": "...", "branch": "...", "address": "...", "phone": "..."},
  "transaction": {"date": "...", "time": "...", "receipt_number": "...", "till_number": "...", "cashier": "..."},
  "items": [
    {"name": "...", "category": "...", "quantity": 1, "unit_price": 1.05, "total_price": 1.05, "vat_code": "0"}
  ],
  "totals": {"item_count": 8, "subtotal": 15.31, "vat_breakdown": [...], "total": 15.31},
  "payment": {"method": "CARD", "card_type": "...", "card_last4": "...", "amount_authorised": 15.31}
}
```

This is exactly what's printed on the matching image — useful as a target
for key-information-extraction or full receipt-to-JSON models.

## How the "photographed" look is made (`receipt_gen/augment.py`)

1. Soft wavy crease/fold shadows baked into the paper
2. Slight rotation + perspective skew (camera angle)
3. Composited onto a procedurally generated surface (wood/worktop/desk) with a drop shadow
4. Uneven lighting (single light-source gradient) + vignette
5. Sensor noise + slight focus blur
6. JPEG re-encode at a random quality to bake in compression artefacts

Tune the ranges directly in `augment.py` if you want noisier/cleaner output,
or pass `--style clean` to skip the photo step entirely.
