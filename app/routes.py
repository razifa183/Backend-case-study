from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from .models import db, Product, Inventory, Warehouse, Supplier, SupplierProduct, Sale

routes = Blueprint('routes', __name__)

@routes.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    try:
        thirty_days = datetime.utcnow() - timedelta(days=30)

        active_product_ids = db.session.query(Sale.product_id).join(Warehouse).filter(
            Warehouse.company_id == company_id,
            Sale.sale_date >= thirty_days
        ).distinct().all()

        active_product_ids = [pid[0] for pid in active_product_ids]

        if not active_product_ids:
            return jsonify({"alerts": [], "total_alerts": 0})

        results = db.session.query(
            Product.id, Product.name, Product.sku, Product.low_stock_threshold,
            Inventory.quantity, Inventory.warehouse_id, Warehouse.name,
            Supplier.id, Supplier.name, Supplier.contact_email
        ).join(Inventory, Product.id == Inventory.product_id
        ).join(Warehouse, Inventory.warehouse_id == Warehouse.id
        ).join(SupplierProduct, Product.id == SupplierProduct.product_id
        ).join(Supplier, Supplier.id == SupplierProduct.supplier_id
        ).filter(
            Warehouse.company_id == company_id,
            Product.id.in_(active_product_ids),
            Inventory.quantity < Product.low_stock_threshold
        ).all()

        alerts = []
        for row in results:
            days_until_stockout = int(row.quantity / 2) if row.quantity else 0
            alerts.append({
                "product_id": row.id,
                "product_name": row.name,
                "sku": row.sku,
                "warehouse_id": row.warehouse_id,
                "warehouse_name": row[6],
                "current_stock": row.quantity,
                "threshold": row.low_stock_threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": {
                    "id": row[7],
                    "name": row[8],
                    "contact_email": row[9]
                }
            })

        return jsonify({"alerts": alerts, "total_alerts": len(alerts)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

