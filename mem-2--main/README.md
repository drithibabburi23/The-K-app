# Member 5 - KarigarConnect Marketplace Module

**Smart Price Guide + Marketplace Logic for Smart India Hackathon 2026**

This is Member 5's contribution to the **KarigarConnect** AI-driven market linkage and smart cataloguing mobile application for marginalized artisans.

---

## Overview

This module provides three key capabilities:

### 1. **Smart Price Guide** 
Generates reasonable selling price ranges for handmade products based on:
- Product category (Textiles, Pottery, Woodcraft, etc.)
- Material used (Cotton, Silk, Terracotta, Teak, etc.)
- Craft type (Handwoven, Hand-carved, Hand-painted, etc.)
- Product complexity and attributes

**Example:**
```python
from member5_marketplace.price_guide import generate_price_guide

product = {
    "product_name": "Handmade Cotton Saree",
    "category": "Textiles",
    "material": "Cotton",
    "craft": "Handwoven",
    "color": "Blue"
}

result = generate_price_guide(product)
# Returns: ₹1,200 - ₹1,600 (Estimated Price Range)
```

### 2. **Marketplace & Product Discovery**
Search and browse marketplace with flexible filtering:
- Search by product name and description
- Filter by category, material, craft, and color
- Retrieve product details with pricing
- View artisan's product catalog

**Example:**
```python
from member5_marketplace.marketplace import search_products, get_product_details

# Search for products
results = search_products(query="cotton saree", category="Textiles")

# Get detailed product information
product_detail = get_product_details("P001")
```

### 3. **Buyer Enquiry System**
Basic buyer-to-artisan communication:
- Create enquiries about products
- Track enquiry status (pending, read, replied, closed)
- Retrieve enquiries for artisans and buyers
- Simple and extensible design

**Example:**
```python
from member5_marketplace.enquiry import (
    create_enquiry,
    get_artisan_enquiries,
    update_enquiry_status
)

# Buyer creates enquiry
enquiry = create_enquiry(
    buyer_id="B001",
    product_id="P001",
    artisan_id="A001",
    message="Is this product available in different colors?"
)

# Artisan retrieves enquiries
artisan_enquiries = get_artisan_enquiries("A001")

# Artisan updates status
update_enquiry_status(enquiry["enquiry"]["enquiry_id"], "replied")
```

---

## Team Integration

This module is part of a larger application with clear responsibility divisions:

| Component | Responsibility |
|-----------|-----------------|
| **Member 2** | AI Product Cataloguing (voice-to-text, description generation, multilingual support) |
| **Member 5** | Smart Price Guide + Marketplace Logic (THIS MODULE) |
| **Member 4** | Main Backend (API, database, authentication) |
| **Other Members** | Frontend/Mobile Application UI |

### Data Flow

```
Member 2 (AI Cataloguing)
   ↓
   Product Information JSON
   {
     "product_name": "Handmade Cotton Saree",
     "category": "Textile",
     "material": "Cotton",
     "craft": "Handwoven",
     "description": "..."
   }
   ↓
Member 5 (This Module)
   ├── Price Guide Generation
   ├── Product Listing/Search
   └── Enquiry Management
   ↓
   Enriched Product JSON with Pricing
   {
     "product": {...},
     "price_guide": {
       "minimum_price": 1200,
       "maximum_price": 1600,
       "currency": "INR"
     }
   }
   ↓
Member 4 (Backend Integration)
   ├── Database Storage
   ├── API Endpoints
   └── Authentication
   ↓
Frontend/Mobile App
```

---

## Architecture

The module is organized as follows:

```
member5_marketplace/
├── __init__.py              # Module entry point
├── price_guide.py           # Smart price guide logic
├── pricing_rules.py         # Pricing factors (easily replaceable)
├── marketplace.py           # Search, discovery, product details
├── enquiry.py               # Buyer enquiry system
├── schemas.py               # Data models and structures
└── exceptions.py            # Custom exceptions

tests/
└── test_member5_marketplace.py  # Comprehensive unit tests

README.md                    # This file
requirements.txt             # Python dependencies
```

### Design Principles

1. **Independent**: Works without external dependencies (uses only Python stdlib)
2. **Modular**: Each component is self-contained and replaceable
3. **Mock-Friendly**: Uses in-memory storage for development/testing
4. **Extensible**: Easy to integrate with Member 4's database
5. **Well-Tested**: Comprehensive unit and integration tests
6. **Type-Hinted**: Clear type annotations for IDE support
7. **Documented**: Docstrings and examples throughout

---

## Pricing Logic

### Category Base Prices

Each product category has a base price range (in INR):

| Category | Min | Max |
|----------|-----|-----|
| Textiles | ₹800 | ₹2,000 |
| Pottery | ₹300 | ₹1,500 |
| Woodcraft | ₹500 | ₹2,500 |
| Paintings | ₹1,000 | ₹5,000 |
| Jewellery | ₹500 | ₹3,000 |
| Handicrafts | ₹400 | ₹2,000 |
| Other | ₹300 | ₹1,000 |

### Multipliers Applied

**Material Multipliers (examples):**
- Silk: 1.5× (premium)
- Cotton: 1.0× (baseline)
- Terracotta: 1.0× (baseline pottery)
- Teak: 1.5× (premium wood)

**Craft Multipliers (examples):**
- Handwoven: 1.3×
- Hand-carved: 1.4×
- Hand-painted: 1.2×
- Handmade: 1.1×

**Complexity Multipliers:**
- Intricate: 1.2×
- Detailed: 1.15×
- Simple: 0.8×

### Price Calculation Formula

```
Final Price Range = Base Price × Material Multiplier × Craft Multiplier × Complexity Multiplier
```

### Confidence Levels

Price confidence is determined by data completeness:

- **High**: All key fields (category, material, craft) provided
- **Medium**: 1-2 key fields missing
- **Low**: Multiple key fields missing

Example output:
```json
{
  "minimum_price": 1200,
  "maximum_price": 1600,
  "currency": "INR",
  "basis": ["Textiles", "Cotton", "Handwoven"],
  "confidence": "high"
}
```

---

## API Reference

### Price Guide

#### `generate_price_guide(product: dict) -> dict`

Generate a price range for a product.

**Input:**
```python
product = {
    "product_name": "Handmade Cotton Saree",  # Required
    "category": "Textiles",                   # Required
    "material": "Cotton",                     # Optional
    "craft": "Handwoven",                     # Optional
    "color": "Blue",                          # Optional
    "description": "...",                     # Optional
    "extra_attributes": {...}                 # Optional
}
```

**Output (Success):**
```python
{
    "success": True,
    "price_guide": {
        "minimum_price": 1200,
        "maximum_price": 1600,
        "currency": "INR",
        "basis": ["Textiles", "Cotton", "Handwoven"],
        "confidence": "high"
    }
}
```

**Output (Error):**
```python
{
    "success": False,
    "error": {
        "code": "INVALID_PRODUCT",
        "message": "Product must have a category"
    }
}
```

---

### Marketplace

#### `search_products(query=None, category=None, material=None, craft=None, color=None) -> dict`

Search and filter products.

**Example:**
```python
results = search_products(
    query="saree",
    category="Textiles",
    material="Cotton"
)
```

**Output:**
```python
{
    "success": True,
    "query": {
        "text": "saree",
        "category": "Textiles",
        "material": "Cotton",
        ...
    },
    "total": 3,
    "products": [
        {
            "product_id": "P001",
            "product_name": "Handmade Cotton Saree",
            "category": "Textiles",
            "material": "Cotton",
            "craft": "Handwoven",
            "color": "Blue",
            "minimum_price": 1200,
            "maximum_price": 1600,
            "currency": "INR",
            "artisan_id": "A001",
            "artisan_name": "Savitri Devi",
            "image_url": "https://..."
        },
        ...
    ]
}
```

#### `get_product_details(product_id: str) -> dict`

Get complete details for a product.

**Example:**
```python
product = get_product_details("P001")
```

**Output:**
```python
{
    "success": True,
    "product": {
        "product_id": "P001",
        "product_name": "Handmade Cotton Saree",
        "category": "Textiles",
        "material": "Cotton",
        "craft": "Handwoven",
        "color": "Blue",
        "description": "A beautiful handwoven blue cotton saree...",
        "minimum_price": 1200,
        "maximum_price": 1600,
        "currency": "INR",
        "artisan_id": "A001",
        "artisan_name": "Savitri Devi",
        "image_url": "https://..."
    }
}
```

#### `get_categories() -> dict`

Get all available product categories.

#### `get_artisan_products(artisan_id: str) -> dict`

Get all products from a specific artisan.

---

### Enquiry System

#### `create_enquiry(buyer_id: str, product_id: str, artisan_id: str, message: str) -> dict`

Create a new enquiry.

**Validation:**
- `buyer_id`: Required, non-empty string
- `product_id`: Required, non-empty string
- `artisan_id`: Required, non-empty string
- `message`: Required, 5-1000 characters

**Example:**
```python
enquiry = create_enquiry(
    buyer_id="B001",
    product_id="P001",
    artisan_id="A001",
    message="Is this product available in stock?"
)
```

**Output:**
```python
{
    "success": True,
    "enquiry": {
        "enquiry_id": "ENQ-ABC123DEF456",
        "buyer_id": "B001",
        "product_id": "P001",
        "artisan_id": "A001",
        "message": "Is this product available in stock?",
        "status": "pending",
        "created_at": "2026-01-15T10:30:00",
        "updated_at": "2026-01-15T10:30:00"
    }
}
```

#### `get_enquiry(enquiry_id: str) -> dict`

Get details of a specific enquiry.

#### `get_artisan_enquiries(artisan_id: str) -> dict`

Get all enquiries received by an artisan.

**Output:**
```python
{
    "success": True,
    "artisan_id": "A001",
    "total": 5,
    "enquiries": [
        {...},  # Enquiry 1
        {...},  # Enquiry 2
        ...
    ]
}
```

#### `get_buyer_enquiries(buyer_id: str) -> dict`

Get all enquiries made by a buyer.

#### `update_enquiry_status(enquiry_id: str, new_status: str) -> dict`

Update enquiry status.

**Valid statuses:**
- `"pending"` - Initial status
- `"read"` - Artisan has read the enquiry
- `"replied"` - Artisan has replied
- `"closed"` - Conversation is closed

**Example:**
```python
result = update_enquiry_status("ENQ-ABC123DEF456", "replied")
```

#### `get_product_enquiries(product_id: str) -> dict`

Get all enquiries for a specific product.

---

## Mock Data for Development

The module includes mock product and enquiry data for testing and development:

**Mock Products:**
```python
from member5_marketplace.marketplace import MOCK_PRODUCTS

# MOCK_PRODUCTS contains:
# - P001: Handmade Cotton Saree (₹1,200 - ₹1,600)
# - P002: Handwoven Silk Saree (₹1,800 - ₹2,400)
# - P003: Terracotta Pot (₹300 - ₹1,500)
# - P004: Hand-carved Wooden Box (₹750 - ₹3,750)
# - P005: Traditional Painting (₹1,000 - ₹6,500)
# - P006: Silver Jewelry Set (₹650 - ₹3,900)
# - P007: Jute Bag (₹360 - ₹1,800)
```

These can be replaced with Member 4's database queries later.

---

## Testing

Comprehensive unit tests are provided in `tests/test_member5_marketplace.py`.

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=member5_marketplace

# Run specific test class
python -m pytest tests/test_member5_marketplace.py::TestPriceGuide -v

# Run specific test
python -m pytest tests/test_member5_marketplace.py::TestPriceGuide::test_textile_cotton_handwoven -v
```

### Test Coverage

- **Price Guide**: 10 test cases
- **Marketplace Search**: 8 test cases
- **Product Details**: 4 test cases
- **Enquiry System**: 14 test cases
- **Integration Tests**: 2 complete workflow tests

Total: **38+ unit and integration tests**

---

## Integration with Member 4's Backend

Member 4 can easily integrate this module into the main backend:

### 1. Import and Use

```python
from member5_marketplace.price_guide import generate_price_guide
from member5_marketplace.marketplace import search_products, get_product_details
from member5_marketplace.enquiry import (
    create_enquiry,
    get_artisan_enquiries,
    update_enquiry_status
)
```

### 2. Replace Mock Data with Database

Update `marketplace.py` and `enquiry.py` to use actual database queries instead of mock data:

```python
# Current (mock):
def _get_all_products():
    return MOCK_PRODUCTS.copy()

# Proposed (database):
def _get_all_products():
    from your_database import Product
    return Product.query.all()
```

### 3. API Endpoint Example (Flask/FastAPI)

```python
from flask import Flask, request, jsonify
from member5_marketplace.marketplace import search_products, get_product_details
from member5_marketplace.enquiry import create_enquiry

app = Flask(__name__)

@app.route('/api/marketplace/search', methods=['GET'])
def search():
    query = request.args.get('q')
    category = request.args.get('category')
    return search_products(query=query, category=category)

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    return get_product_details(product_id)

@app.route('/api/enquiries', methods=['POST'])
def create_inquiry():
    data = request.json
    return create_enquiry(
        buyer_id=data['buyer_id'],
        product_id=data['product_id'],
        artisan_id=data['artisan_id'],
        message=data['message']
    )
```

### 4. Database Schema Recommendations

**Products Table:**
```sql
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    material VARCHAR(100),
    craft VARCHAR(100),
    color VARCHAR(100),
    description TEXT,
    artisan_id VARCHAR(50),
    artisan_name VARCHAR(255),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Enquiries Table:**
```sql
CREATE TABLE enquiries (
    enquiry_id VARCHAR(50) PRIMARY KEY,
    buyer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    artisan_id VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_artisan (artisan_id),
    INDEX idx_buyer (buyer_id)
);
```

---

## Extending the Pricing Rules

The pricing logic is designed to be easily updatable. To modify pricing:

### 1. Update Category Base Prices

Edit `pricing_rules.py`:
```python
CATEGORY_BASE_PRICES = {
    Category.TEXTILES: (800, 2000),  # Modify this range
    Category.POTTERY: (300, 1500),
    ...
}
```

### 2. Add New Materials

```python
MATERIAL_MULTIPLIERS = {
    "Cotton": 1.0,
    "Silk": 1.5,
    "Your_New_Material": 1.3,  # Add here
    ...
}
```

### 3. Add New Craft Types

```python
CRAFT_MULTIPLIERS = {
    "Handwoven": 1.3,
    "Hand-carved": 1.4,
    "Your_New_Craft": 1.2,  # Add here
    ...
}
```

### 4. Replace with Real Market Data API

Future enhancement: Replace mock calculations with API calls to real market data:

```python
def generate_price_guide(product):
    # Call real market data API
    market_data = get_market_data_from_api(product)
    return {
        "minimum_price": market_data["min"],
        "maximum_price": market_data["max"],
        ...
    }
```

---

## Error Handling

All functions return structured error responses:

```python
{
    "success": False,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message"
    }
}
```

**Common Error Codes:**
- `INVALID_PRODUCT`: Product data is invalid
- `INVALID_PRICE`: Price calculation failed
- `PRODUCT_NOT_FOUND`: Product ID doesn't exist
- `INVALID_ENQUIRY`: Enquiry data is invalid
- `ENQUIRY_NOT_FOUND`: Enquiry ID doesn't exist
- `INVALID_STATUS`: Enquiry status is not valid
- `INVALID_SEARCH`: Search parameters are invalid
- `INTERNAL_ERROR`: Unexpected error occurred

---

## Logging

The module includes comprehensive logging for debugging:

```python
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("member5_marketplace")
```

Logged events:
- Product price guide generation
- Search queries and results
- Enquiry creation and updates
- Errors and warnings

---

## Future Enhancements

1. **Real Market Data Integration**: Replace mock pricing with actual market datasets
2. **Machine Learning**: Add ML-based price prediction
3. **Multi-language Support**: Integrate with Member 2's multilingual cataloguing
4. **Advanced Search**: Full-text search, faceted filtering
5. **Recommendation Engine**: Suggest products based on buyer behavior
6. **Analytics**: Track popular products, pricing trends
7. **Review System**: Add product reviews and ratings
8. **Real-time Chat**: Upgrade from enquiries to real-time messaging

---

## Dependencies

**Core:**
- Python 3.7+
- No external dependencies (uses only Python stdlib)

**Development & Testing:**
- pytest
- pytest-cov
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

Install all:
```bash
pip install -r requirements.txt
```

---

## License

This is part of the Smart India Hackathon 2026 project.

---

## Contact & Support

For integration questions or issues:
- This module: Member 5
- Main Backend: Member 4
- AI Cataloguing: Member 2
- Frontend: Other Team Members

---

## Quick Start Example

Complete example showing the full workflow:

```python
# 1. AI Module (Member 2) produces product info
ai_product = {
    "product_name": "Handmade Khadi Saree",
    "category": "Textiles",
    "material": "Khadi",
    "craft": "Handwoven",
    "color": "Cream",
    "description": "Traditional khadi with natural dyes"
}

# 2. Member 5 generates price
from member5_marketplace.price_guide import generate_price_guide
price_result = generate_price_guide(ai_product)
print(f"Price: ₹{price_result['price_guide']['minimum_price']}-{price_result['price_guide']['maximum_price']}")

# 3. Frontend searches products
from member5_marketplace.marketplace import search_products
search_results = search_products(query="khadi")
for product in search_results['products']:
    print(f"{product['product_name']}: ₹{product['minimum_price']}-{product['maximum_price']}")

# 4. Buyer views details
from member5_marketplace.marketplace import get_product_details
product_details = get_product_details(search_results['products'][0]['product_id'])
print(product_details['product'])

# 5. Buyer sends enquiry
from member5_marketplace.enquiry import create_enquiry
enquiry = create_enquiry(
    buyer_id="B001",
    product_id=product_details['product']['product_id'],
    artisan_id=product_details['product']['artisan_id'],
    message="Can you make it in a different size?"
)

# 6. Artisan receives and responds to enquiry
from member5_marketplace.enquiry import get_artisan_enquiries, update_enquiry_status
artisan_enquiries = get_artisan_enquiries(product_details['product']['artisan_id'])
if artisan_enquiries['success']:
    update_enquiry_status(enquiry['enquiry']['enquiry_id'], "replied")

print("✓ Complete workflow executed successfully!")
```

---

**Version:** 1.0.0  
**Last Updated:** 2026-09-09  
**Member 5 Contribution - SIH 2026**
