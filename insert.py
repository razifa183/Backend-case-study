from app.models import db, Product, Inventory, Warehouse, Supplier, SupplierProduct, Sale
from main import app
from datetime import datetime

with app.app_context():
    # Warehouse
    w = Warehouse(name="Main Warehouse", company_id=2)
    db.session.add(w)
    db.session.commit()

    # Product
    p = Product(name="Widget B", sku="WID-002", price=99.79, low_stock_threshold=10)
    db.session.add(p)
    db.session.commit()

    # Inventory
    i = Inventory(product_id=p.id, warehouse_id=w.id, quantity=7)
    db.session.add(i)

    # Supplier
    s = Supplier(name="Supplier crop", contact_email="order@supplier.com")
    db.session.add(s)
    db.session.commit()

    # Supplier–Product Link
    sp = SupplierProduct(supplier_id=s.id, product_id=p.id)
    db.session.add(sp)

    # Sale (recent)
    sale = Sale(product_id=p.id, warehouse_id=w.id, sale_date=datetime.utcnow())
    db.session.add(sale)

    db.session.commit()

    print("Dummy data inserted successfully!")
