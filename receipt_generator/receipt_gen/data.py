"""
Item catalog and store profile data used to generate synthetic UK
supermarket-style receipts. All brand names are used only as plain text
style references (no logos/artwork are reproduced) so the generator stays
purely a layout/format mimic for synthetic dataset purposes.
"""

import random
import string

# ---------------------------------------------------------------------------
# Store style profiles
# ---------------------------------------------------------------------------
# Each profile defines the cosmetic conventions of a receipt: header text,
# accent colour, VAT registration format, footer message, etc. These are
# generic layout conventions (common to UK till receipts) rather than any
# reproduction of a real logo or trademarked artwork.

STORE_PROFILES = {
    "asda": {
        "name": "ASDA",
        "legal_name": "Asda Stores Limited",
        "accent_color": (0, 122, 62),       # ASDA-ish green
        "header_font_scale": 1.9,
        "footer_lines": [
            "Thank you for shopping with us",
            "VAT Reg No: 343 9468 47",
        ],
        # Each branch carries its own town/postcode so the printed
        # address always matches the branch name.
        "branches": [
            {"name": "Leeds Killingbeck Superstore", "town": "Leeds", "postcode": "LS9 0PQ"},
            {"name": "Manchester Eastlands Store", "town": "Manchester", "postcode": "M11 4KL"},
            {"name": "Bristol Eastville Store", "town": "Bristol", "postcode": "BS5 6TR"},
            {"name": "Sheffield Catcliffe Store", "town": "Sheffield", "postcode": "S60 5TZ"},
            {"name": "Wolverhampton Store", "town": "Wolverhampton", "postcode": "WV1 3AB"},
            {"name": "Coventry Walsgrave Store", "town": "Coventry", "postcode": "CV2 2HJ"},
        ],
    },
    "aldi": {
        "name": "ALDI",
        "legal_name": "Aldi Stores Limited",
        "accent_color": (0, 61, 132),        # Aldi-ish blue
        "header_font_scale": 1.9,
        "footer_lines": [
            "Thank you for shopping at Aldi",
            "VAT Reg No: 932 5821 19",
        ],
        "branches": [
            {"name": "Aldi Nottingham Store", "town": "Nottingham", "postcode": "NG7 2UH"},
            {"name": "Aldi Romford Store", "town": "Romford", "postcode": "RM1 3AG"},
            {"name": "Aldi Cardiff Bay Store", "town": "Cardiff", "postcode": "CF10 4PA"},
            {"name": "Aldi Preston Store", "town": "Preston", "postcode": "PR1 8AA"},
            {"name": "Aldi Dundee Store", "town": "Dundee", "postcode": "DD1 4HN"},
            {"name": "Aldi Swindon Store", "town": "Swindon", "postcode": "SN1 1QF"},
        ],
    },
}

STREET_NAMES = [
    "High Street", "Station Road", "Victoria Road", "Church Lane",
    "Mill Lane", "Park Avenue", "Queens Road", "King Street",
    "Albert Road", "Manor Way", "Greenfield Road", "Orchard Way",
]

# ---------------------------------------------------------------------------
# Item catalog: (name, category, min_price, max_price) in GBP
# ---------------------------------------------------------------------------
ITEM_CATALOG = [
    # Fruit & Veg
    ("Bananas 5 Pack", "Fruit & Veg", 0.95, 1.15),
    ("Loose Bananas", "Fruit & Veg", 0.20, 0.30),
    ("Pink Lady Apples 6 Pack", "Fruit & Veg", 1.80, 2.40),
    ("Conference Pears 4 Pack", "Fruit & Veg", 1.30, 1.70),
    ("Seedless Red Grapes 500g", "Fruit & Veg", 1.80, 2.50),
    ("Carrots 1kg", "Fruit & Veg", 0.45, 0.65),
    ("White Potatoes 2.5kg", "Fruit & Veg", 1.80, 2.40),
    ("Broccoli Head", "Fruit & Veg", 0.65, 0.95),
    ("Iceberg Lettuce", "Fruit & Veg", 0.45, 0.65),
    ("Vine Tomatoes 400g", "Fruit & Veg", 1.10, 1.50),
    ("Cucumber", "Fruit & Veg", 0.50, 0.70),
    ("Red Onions 1kg", "Fruit & Veg", 0.85, 1.15),
    ("Garlic Bulb", "Fruit & Veg", 0.40, 0.60),
    ("Avocados 2 Pack", "Fruit & Veg", 1.60, 2.10),
    ("Blueberries 150g", "Fruit & Veg", 1.70, 2.20),
    ("Strawberries 400g", "Fruit & Veg", 2.20, 3.00),
    ("Mushrooms Chestnut 250g", "Fruit & Veg", 0.95, 1.30),
    ("Sweet Peppers 3 Pack", "Fruit & Veg", 1.40, 1.90),
    # Bakery
    ("White Sliced Bread 800g", "Bakery", 0.95, 1.30),
    ("Wholemeal Bread 800g", "Bakery", 1.05, 1.40),
    ("Bagels 5 Pack", "Bakery", 0.85, 1.20),
    ("White Bread Rolls 6 Pack", "Bakery", 0.85, 1.15),
    ("Croissants 4 Pack", "Bakery", 1.20, 1.60),
    ("Tortilla Wraps 8 Pack", "Bakery", 1.00, 1.40),
    ("Crumpets 9 Pack", "Bakery", 0.85, 1.15),
    ("Garlic Baguette", "Bakery", 0.95, 1.30),
    ("Chocolate Muffins 4 Pack", "Bakery", 1.30, 1.80),
    # Dairy & Eggs
    ("Whole Milk 2 Pints", "Dairy & Eggs", 1.30, 1.65),
    ("Semi Skimmed Milk 4 Pints", "Dairy & Eggs", 1.50, 1.85),
    ("Free Range Eggs 6 Pack", "Dairy & Eggs", 1.50, 2.10),
    ("Free Range Eggs 12 Pack", "Dairy & Eggs", 2.60, 3.40),
    ("Mature Cheddar 400g", "Dairy & Eggs", 2.60, 3.40),
    ("Mild Cheddar 250g", "Dairy & Eggs", 1.80, 2.30),
    ("Salted Butter 250g", "Dairy & Eggs", 1.80, 2.40),
    ("Greek Style Yogurt 500g", "Dairy & Eggs", 1.10, 1.50),
    ("Natural Yogurt 1kg", "Dairy & Eggs", 1.30, 1.70),
    ("Single Cream 300ml", "Dairy & Eggs", 1.10, 1.45),
    ("Mozzarella Ball 125g", "Dairy & Eggs", 0.85, 1.15),
    ("Margarine Spread 500g", "Dairy & Eggs", 1.50, 2.00),
    # Meat & Fish
    ("Chicken Breast Fillets 650g", "Meat & Fish", 3.80, 4.80),
    ("British Beef Mince 500g", "Meat & Fish", 3.20, 4.20),
    ("Smoked Bacon 300g", "Meat & Fish", 2.40, 3.20),
    ("Pork Sausages 8 Pack", "Meat & Fish", 2.20, 3.00),
    ("Scottish Salmon Fillets 2 Pack", "Meat & Fish", 4.50, 5.80),
    ("Cooked Ham Slices 200g", "Meat & Fish", 1.80, 2.40),
    ("Chicken Thighs 1kg", "Meat & Fish", 3.00, 3.80),
    ("Beef Burgers 4 Pack", "Meat & Fish", 2.50, 3.30),
    # Frozen
    ("Frozen Peas 1kg", "Frozen", 1.10, 1.50),
    ("Oven Chips 1.5kg", "Frozen", 1.50, 2.00),
    ("Fish Fingers 10 Pack", "Frozen", 1.90, 2.50),
    ("Margherita Pizza", "Frozen", 1.50, 2.20),
    ("Vanilla Ice Cream 900ml", "Frozen", 1.80, 2.50),
    ("Frozen Mixed Berries 500g", "Frozen", 2.00, 2.70),
    ("Garlic Bread Twin Pack", "Frozen", 1.30, 1.80),
    # Tins & Packets
    ("Baked Beans 415g", "Tins & Packets", 0.45, 0.65),
    ("Chopped Tomatoes 400g", "Tins & Packets", 0.40, 0.60),
    ("Tuna Chunks in Brine 145g", "Tins & Packets", 0.85, 1.15),
    ("Penne Pasta 500g", "Tins & Packets", 0.55, 0.80),
    ("Basmati Rice 1kg", "Tins & Packets", 1.60, 2.20),
    ("Cornflakes 500g", "Tins & Packets", 1.50, 2.00),
    ("Porridge Oats 1kg", "Tins & Packets", 1.20, 1.60),
    ("Tomato Soup 400g", "Tins & Packets", 0.55, 0.80),
    ("Instant Noodles 5 Pack", "Tins & Packets", 1.00, 1.40),
    ("Sunflower Oil 1L", "Tins & Packets", 1.80, 2.40),
    ("Plain Flour 1.5kg", "Tins & Packets", 0.85, 1.15),
    ("Granulated Sugar 1kg", "Tins & Packets", 0.95, 1.25),
    # Drinks
    ("Orange Juice 1L", "Drinks", 1.10, 1.50),
    ("Cola 2L Bottle", "Drinks", 1.50, 2.00),
    ("Still Water 6x500ml", "Drinks", 1.50, 2.00),
    ("Sparkling Water 1L", "Drinks", 0.65, 0.95),
    ("Ground Coffee 200g", "Drinks", 2.80, 3.60),
    ("Tea Bags 80 Pack", "Drinks", 2.20, 2.90),
    ("Squash Blackcurrant 1L", "Drinks", 1.10, 1.50),
    ("Lager 4x440ml", "Drinks", 3.50, 4.50),
    ("Red Wine 75cl", "Drinks", 5.50, 8.00),
    # Snacks
    ("Tortilla Chips 200g", "Snacks", 1.10, 1.50),
    ("Salted Crisps 6 Pack", "Snacks", 1.50, 2.00),
    ("Milk Chocolate Bar 200g", "Snacks", 1.30, 1.80),
    ("Digestive Biscuits 400g", "Snacks", 0.95, 1.30),
    ("Mixed Nuts 200g", "Snacks", 1.80, 2.40),
    ("Cereal Bars 6 Pack", "Snacks", 1.80, 2.40),
    ("Popcorn Sharing Bag 150g", "Snacks", 1.10, 1.50),
    # Household
    ("Toilet Roll 9 Pack", "Household", 3.80, 4.80),
    ("Kitchen Towel 4 Pack", "Household", 2.20, 2.90),
    ("Washing Up Liquid 500ml", "Household", 0.95, 1.30),
    ("Laundry Capsules 19 Pack", "Household", 4.50, 5.80),
    ("All Purpose Cleaner Spray", "Household", 1.10, 1.50),
    ("Bin Bags 20 Pack", "Household", 1.50, 2.00),
    ("Dishwasher Tablets 30 Pack", "Household", 4.00, 5.20),
    ("Foil Roll 30m", "Household", 2.00, 2.70),
    # Toiletries
    ("Shampoo 400ml", "Toiletries", 1.80, 2.60),
    ("Shower Gel 500ml", "Toiletries", 1.50, 2.20),
    ("Toothpaste 100ml", "Toiletries", 1.20, 1.80),
    ("Deodorant Spray 150ml", "Toiletries", 1.80, 2.50),
    ("Hand Wash 250ml", "Toiletries", 0.95, 1.40),
    ("Paracetamol 16 Pack", "Toiletries", 0.55, 0.85),
    # Pet
    ("Dog Food Tins 6 Pack", "Pet", 2.50, 3.40),
    ("Cat Food Pouches 12 Pack", "Pet", 3.00, 4.00),
    ("Cat Litter 10L", "Pet", 3.50, 4.50),
]

VAT_CODES = {
    "Fruit & Veg": "0",       # zero rated
    "Bakery": "0",
    "Dairy & Eggs": "0",
    "Meat & Fish": "0",
    "Frozen": "0",
    "Tins & Packets": "0",
    "Drinks": "0",
    "Snacks": "A",            # standard rated (confectionery/crisps etc.)
    "Household": "A",
    "Toiletries": "A",
    "Pet": "A",
}

VAT_RATES = {"0": 0.0, "A": 0.20}
VAT_LABELS = {"0": "Zero Rated", "A": "Standard Rate 20.0%"}

CARD_TYPES = ["VISA DEBIT", "MASTERCARD DEBIT", "VISA CREDIT", "MAESTRO"]

CASHIER_NAMES = [
    "JANE", "MARK", "SARAH", "PRIYA", "TOM", "AMY", "DAVID", "LUCY",
    "OMAR", "FREYA", "JOSH", "ELLA", "RYAN", "MEGAN",
]


def random_receipt_number():
    return "".join(random.choices(string.digits, k=4)) + "-" + \
           "".join(random.choices(string.digits, k=6))


def random_card_last4():
    return "".join(random.choices(string.digits, k=4))


def random_phone():
    return "0" + "".join(random.choices(string.digits, k=3)) + " " + \
           "".join(random.choices(string.digits, k=3)) + " " + \
           "".join(random.choices(string.digits, k=4))
