import logging

from nameko.events import event_handler, EventDispatcher
from nameko.rpc import rpc

from products import dependencies, schemas


logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()
    event_dispatcher = EventDispatcher()

    @rpc
    def get(self, product_id):
        product = self.storage.get(product_id)
        return schemas.Product().dump(product).data

    @rpc
    def list(self):
        products = self.storage.list()
        return schemas.Product(many=True).dump(products).data

    @rpc
    def create(self, product):
        product = schemas.Product(strict=True).load(product).data
        self.storage.create(product)
        self.event_dispatcher('product_created', {
            'product': product,
        })

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])
