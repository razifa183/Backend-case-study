Part 1: Code Review & Debugging
Issues Identified
1. No validation on input may lead to runtime errors
2. SKU uniqueness not found 
3. If second commit(inventory) fails, product is still created which lead to inconsistency.
4. No error handling is done
5. He assume all fields are mandatory but some feild might be optional

Corrected Code 

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()

    # Validation of input fields
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return {"error": f"Missing fields: {', '.join(missing)}"}, 400

    # unique SKU
    if Product.query.filter_by(sku=data['sku']).first():
        return {"error": "SKU must be unique"}, 400

    try:
        product = Product(
            name=data.get('name'),
            sku=data.get('sku'),
            price=float(data.get('price', 0.0))  # assuming price default = 0.0
        )
        db.session.add(product)
        db.session.flush()  # Get product.id without committing

        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data.get('warehouse_id'),
            quantity=data.get('initial_quantity', 0)
        )
        db.session.add(inventory)
        db.session.commit()

        return {"message": "Product created", "product_id": product.id}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500          // error handling 



Part 2: Database Design
SQL Notation

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    company_id INTEGER REFERENCES companies(id)
);


CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    price DECIMAL(10, 2) DEFAULT 0.0,
    type TEXT DEFAULT 'standard' -- 'bundle' or 'standard'
);


CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    warehouse_id INTEGER REFERENCES warehouses(id),
    quantity INTEGER DEFAULT 0,
    UNIQUE(product_id, warehouse_id)
);


CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    warehouse_id INTEGER REFERENCES warehouses(id),
    quantity_before INTEGER,
    quantity_after INTEGER,
    change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);


CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    contact_email TEXT
);

//SupplierProducts (Many-to-Many)
CREATE TABLE supplier_products (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(id),
    product_id INTEGER REFERENCES products(id)
);

//Product Bundles (relation)
CREATE TABLE product_bundles (
    id SERIAL PRIMARY KEY,
    bundle_id INTEGER REFERENCES products(id),
    component_id INTEGER REFERENCES products(id),
    quantity INTEGER DEFAULT 1
);

Questions for product team 

1. Can a product belong to multiple suppliers?
2. Does warehouses have location?
3. Bundles have price ?
4. Is bundles are derived from its components?

Design Features

    1.Indexes on foreign keys

    2.UNIQUE(sku) and UNIQUE(product_id, warehouse_id) for data consistency

    3.Recursive structure for bundles

    4.inventory_logs enables stock change tracking

Part 3: API Implementation – Low Stock Alert

I have made some assumptions as follows:
1. Each product has a low_stock_threshold field
2. Only products with sales in the last 30 days are considered "active"

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    try:
        # Get active products
        thirty_days = datetime.utcnow() - timedelta(days=30)

        active_products = db.session.query(Sale.product_id).join(Warehouse).filter(
            Warehouse.company_id == company_id,
            Sale.sale_date >= thirty_days
        ).distinct().subquery()

        # Join inventory to get stock info
        low_stock = db.session.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.sku,
            Inventory.warehouse_id,
            Warehouse.name.label("warehouse_name"),
            Inventory.quantity.label("current_stock"),
            Product.low_stock_threshold.label("threshold"),
            Supplier.id.label("supplier_id"),
            Supplier.name.label("supplier_name"),
            Supplier.contact_email
        ).join(Inventory, Product.id == Inventory.product_id
        ).join(Warehouse, Inventory.warehouse_id == Warehouse.id
        ).join(SupplierProducts, SupplierProducts.product_id == Product.id
        ).join(Supplier, Supplier.id == SupplierProducts.supplier_id
        ).filter(
            Product.id.in_(active_products),
            Inventory.quantity < Product.low_stock_threshold,
            Warehouse.company_id == company_id
        ).all()

        alerts = []
        for row in low_stock:
            days_until_stockout = int(row.current_stock / 2)  # Dummy logic
            alerts.append({
                "product_id": row.product_id,
                "product_name": row.product_name,
                "sku": row.sku,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row.warehouse_name,
                "current_stock": row.current_stock,
                "threshold": row.threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": {
                    "id": row.supplier_id,
                    "name": row.supplier_name,
                    "contact_email": row.contact_email
                }
            })

        return jsonify({"alerts": alerts, "total_alerts": len(alerts)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



