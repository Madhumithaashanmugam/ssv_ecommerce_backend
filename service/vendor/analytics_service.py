from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, Date
from models.customer.order import Order, OrderStatus
from models.vendor.items import Item
from models.customer.user import User
from models.vendor.offline_orders import OfflineOrder
from typing import Dict
from datetime import date, timedelta

def get_analytics_data(db: Session) -> Dict:
    today = date.today()
    three_days_ago = today - timedelta(days=3)
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)


    total_online_orders = db.query(func.count(Order.id)).scalar()
    total_offline_orders = db.query(func.count(OfflineOrder.id)).scalar()
    total_orders = total_online_orders + total_offline_orders

    total_online_revenue = db.query(func.sum(Order.total_price)).scalar() or 0
    total_offline_revenue = db.query(func.sum(OfflineOrder.amount_paid)).scalar() or 0
    total_revenue_raw = total_online_revenue + total_offline_revenue

    # --- RETURNS ---
    online_returned_orders = db.query(Order).filter(Order.order_status == OrderStatus.returned).all()
    online_returns_value = sum(order.total_price for order in online_returned_orders)

    offline_returned_orders = db.query(OfflineOrder).filter(OfflineOrder.is_returned == True).all()
    offline_returns_value = sum(order.amount_paid for order in offline_returned_orders)

    total_returns_value = online_returns_value + offline_returns_value

    # Adjust total revenue after returns
    net_revenue = total_revenue_raw - total_returns_value
    avg_order_value = net_revenue / total_orders if total_orders else 0

    # --- ORDER STATUS COUNTS (INCLUDING OFFLINE RETURNS) ---
    status_counts = (
        db.query(Order.order_status, func.count(Order.id))
        .group_by(Order.order_status)
        .all()
    )
    order_status_counts_dict = {status.value: count for status, count in status_counts}

    offline_returned_count = db.query(func.count(OfflineOrder.id)).filter(OfflineOrder.is_returned == True).scalar()
    if "Returned" in order_status_counts_dict:
        order_status_counts_dict["Returned"] += offline_returned_count
    else:
        order_status_counts_dict["Returned"] = offline_returned_count

    order_status_counts = [
        {"status": status, "count": count} for status, count in order_status_counts_dict.items()
    ]

    # --- REVENUE PER STATUS (ONLINE ONLY) ---
    revenue_status = (
        db.query(Order.order_status, func.sum(Order.total_price))
        .group_by(Order.order_status)
        .all()
    )
    revenue_per_status = [
        {"status": status.value, "revenue": float(revenue or 0)} for status, revenue in revenue_status
    ]

    # --- TOP CUSTOMERS ---
    top_customers_value = (
        db.query(User.name, func.sum(Order.total_price).label("total"))
        .join(User, Order.user_id == User.id)
        .group_by(User.name)
        .order_by(desc("total"))
        .limit(5)
        .all()
    )
    top_customers_by_value = [
        {"customer_name": name, "total_order_value": float(total)} for name, total in top_customers_value
    ]

    top_customers_orders = (
        db.query(User.name, func.count(Order.id).label("order_count"))
        .join(User, Order.user_id == User.id)
        .group_by(User.name)
        .order_by(desc("order_count"))
        .limit(5)
        .all()
    )
    top_customers_by_orders = [
        {"customer_name": name, "order_count": count} for name, count in top_customers_orders
    ]

    # --- TIME-BASED ANALYTICS ---
    def time_grouped_data(period: str):
        date_expr = func.date_trunc(period, Order.created_datetime).label("period")
        return db.query(date_expr, func.count(Order.id), func.sum(Order.total_price))\
                 .group_by("period")\
                 .order_by("period")\
                 .all()

    def format_grouped(grouped):
        return [
            {
                "date": period.date(),
                "order_count": count,
                "revenue": float(revenue or 0),
            }
            for period, count, revenue in grouped
        ]

    orders_per_day = format_grouped(time_grouped_data("day"))
    orders_per_week = format_grouped(time_grouped_data("week"))
    orders_per_month = format_grouped(time_grouped_data("month"))

    # --- REVENUE BY TIMEFRAME ---
    def adjusted_revenue(filter_date):
        total = db.query(func.sum(Order.total_price))\
                  .filter(func.date(Order.created_datetime) >= filter_date).scalar() or 0
        returned = db.query(func.sum(Order.total_price))\
                     .filter(func.date(Order.created_datetime) >= filter_date)\
                     .filter(Order.order_status == OrderStatus.returned).scalar() or 0
        return total - (returned or 0)

    revenue_today = adjusted_revenue(today)
    revenue_last_3_days = adjusted_revenue(three_days_ago)
    revenue_last_week = adjusted_revenue(seven_days_ago)
    revenue_last_month = adjusted_revenue(thirty_days_ago)

    first_order_date = db.query(func.min(Order.created_datetime)).scalar()
    revenue_from_start = (
        db.query(func.sum(Order.total_price))
        .filter(Order.created_datetime >= first_order_date)
        .scalar() or 0
    ) - total_returns_value

    # --- ORDERS IN TIME RANGES ---
    def fetch_orders_after(start_date):
        return [
            {
                "order_id": order.id,
                "customer_name": user.name,
                "date": order.created_datetime.strftime("%Y-%m-%d"),
                "status": order.order_status.value,
                "amount": float(order.total_price),
            }
            for order, user in db.query(Order, User)
            .join(User, Order.user_id == User.id)
            .filter(Order.created_datetime >= start_date)
            .order_by(Order.created_datetime.desc())
            .all()
        ]

    orders_today = fetch_orders_after(today)
    orders_last_3_days = fetch_orders_after(three_days_ago)
    orders_last_week = fetch_orders_after(seven_days_ago)
    orders_last_month = fetch_orders_after(thirty_days_ago)

    # --- STOCK ---
    total_products = db.query(func.count(Item.id)).scalar()
    stock_levels = [
        {"item_id": item.id, "item_name": item.item_name, "quantity": item.quantity}
        for item in db.query(Item).all()
    ]
    out_of_stock_items = [
        {"item_id": item.id, "item_name": item.item_name, "quantity": item.quantity}
        for item in db.query(Item).filter(Item.quantity <= 5).all()
    ]
    potential_revenue = db.query(func.sum(Item.final_price * Item.quantity)).scalar() or 0

    # --- BEST SELLING PRODUCTS (placeholder logic) ---
    best_selling = (
        db.query(
            Item.id,
            Item.item_name,
            Item.quantity,
            (Item.final_price * Item.quantity).label("revenue")
        )
        .order_by(desc("revenue"))
        .limit(5)
        .all()
    )
    best_selling_products = [
        {
            "item_id": i_id,
            "item_name": name,
            "total_quantity_sold": qty,
            "total_revenue": float(rev),
        }
        for i_id, name, qty, rev in best_selling
    ]

    # --- ALL ORDERS LIST ---
    all_orders = (
        db.query(
            Order.id,
            User.name,
            Order.created_datetime,
            Order.order_status,
            Order.total_price
        )
        .join(User, Order.user_id == User.id)
        .order_by(Order.created_datetime.desc())
        .all()
    )
    all_orders_list = [
        {
            "order_id": oid,
            "customer_name": name,
            "date": created.strftime("%Y-%m-%d"),
            "status": status.value,
            "amount": float(amount)
        }
        for oid, name, created, status, amount in all_orders
    ]

    return {
        "total_orders": total_orders,
        "total_revenue": float(net_revenue),
        "average_order_value": float(avg_order_value),

        "order_status_counts": order_status_counts,
        "revenue_per_status": revenue_per_status,

        "top_customers_by_value": top_customers_by_value,
        "top_customers_by_orders": top_customers_by_orders,

        "orders_per_day": orders_per_day,
        "orders_per_week": orders_per_week,
        "orders_per_month": orders_per_month,

        "revenue_today": float(revenue_today),
        "revenue_last_3_days": float(revenue_last_3_days),
        "revenue_last_week": float(revenue_last_week),
        "revenue_last_month": float(revenue_last_month),
        "revenue_from_first_order": float(revenue_from_start),

        "orders_today": orders_today,
        "orders_last_3_days": orders_last_3_days,
        "orders_last_week": orders_last_week,
        "orders_last_month": orders_last_month,

        "total_products": total_products,
        "stock_levels": stock_levels,
        "out_of_stock_items": out_of_stock_items,
        "potential_revenue_from_stock": float(potential_revenue),

        "best_selling_products": best_selling_products,
        "all_orders": all_orders_list,

        # RETURNS
        "total_returns_value": float(total_returns_value),
        "online_returns_value": float(online_returns_value),
        "offline_returns_value": float(offline_returns_value),
        "returned_orders_count": len(online_returned_orders) + len(offline_returned_orders),
    }