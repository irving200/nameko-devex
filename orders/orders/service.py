import json
from nameko.events import event_handler, EventDispatcher
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from sqlalchemy_filters import apply_pagination

from orders.exceptions import NotFound, ProductNotFound
from orders.models import DeclarativeBase, Order, OrderDetail, Product
from orders.schemas import OrderSchema


class OrdersService:
    name = 'orders'

    db = DatabaseSession(DeclarativeBase)
    event_dispatcher = EventDispatcher()

    @rpc
    def get_orders(self, current_page, page_size):
        orders, pagination = apply_pagination(
            self.db.query(Order),
            page_number=current_page,
            page_size=page_size
        )
        return OrderSchema(many=True).dump(orders).data

    @rpc
    def get_order(self, order_id):
        order = self.db.query(Order).get(order_id)

        if not order:
            raise NotFound('Order with id {} not found'.format(order_id))

        return OrderSchema().dump(order).data

    @rpc
    def create_order(self, order_details):
        products = self.db.query(Product).filter(
            Product.redis_id.in_([item['product_id']for item in order_details])
        ).all()
        valid_products = {prod.redis_id: prod for prod in products}
        for item in order_details:
            if item['product_id'] not in valid_products:
                raise ProductNotFound(
                    "Product Id {}".format(item['product_id'])
                )
        order = Order(
            order_details=[
                OrderDetail(
                    price=order_detail['price'],
                    quantity=order_detail['quantity'],
                    product=valid_products.get(order_detail['product_id'])
                )
                for order_detail in order_details
            ]
        )
        self.db.merge(order)
        self.db.commit()

        order = OrderSchema().dump(order).data
        for order_details in order['order_details']:
            product = order_details.pop("product")
            order_details["product_id"] = product["redis_id"]
        self.event_dispatcher('order_created', {
            'order': order,
        })

        return order

    @rpc
    def update_order(self, order):
        order_details = {
            order_details['id']: order_details
            for order_details in order['order_details']
        }

        order = self.db.query(Order).get(order['id'])

        for order_detail in order.order_details:
            order_detail.price = order_details[order_detail.id]['price']
            order_detail.quantity = order_details[order_detail.id]['quantity']

        self.db.commit()
        return OrderSchema().dump(order).data

    @rpc
    def delete_order(self, order_id):
        order = self.db.query(Order).get(order_id)
        self.db.delete(order)
        self.db.commit()

    @event_handler('products', 'product_created')
    def handle_product_created(self, payload):
        product = Product(
            redis_id=payload['product']['id'],
            title=payload['product']['title'],
            passenger_capacity=payload['product']['passenger_capacity'],
            maximum_speed=payload['product']['maximum_speed'],
            in_stock=payload['product']['in_stock']
        )
        self.db.add(product)
        self.db.commit()
