from marshmallow import Schema, fields


class ProductSchema(Schema):
    id = fields.Int(required=True)
    redis_id = fields.Str(required=True)
    title = fields.Str(required=True)
    passenger_capacity = fields.Int(required=True)
    maximum_speed = fields.Int(required=True)
    in_stock = fields.Int(required=True)


class OrderDetailSchema(Schema):
    id = fields.Int(required=True)
    product_id = fields.Str(required=True)
    price = fields.Decimal(as_string=True)
    product = fields.Nested(ProductSchema)
    quantity = fields.Int()


class OrderSchema(Schema):
    id = fields.Int(required=True)
    order_details = fields.Nested(OrderDetailSchema, many=True)
