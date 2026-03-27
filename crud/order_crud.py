from sqlalchemy.orm import Session
from models.order import Order, OrderDetail


def create_order(db: Session, user_id: int, items: list):

    new_order = Order(user_id=user_id, total_price=0)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    total = 0

    for item in items:

        detail = OrderDetail(
            order_id=new_order.order_id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )

        total += item["price"] * item["quantity"]

        db.add(detail)

    new_order.total_price = total

    db.commit()
    db.refresh(new_order)

    return new_order