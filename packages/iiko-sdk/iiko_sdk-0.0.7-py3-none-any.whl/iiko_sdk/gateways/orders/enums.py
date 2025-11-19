import enum

class DeliveryStatus(str, enum.Enum):
    """ Статус доставки """
    WAITING = 'Waiting'
    ON_WAY = 'OnWay'
    DELIVERED = 'Delivered'

class DeliveryType(str, enum.Enum):
    """ Тип доставки """
    DELIVERY_BY_COURIER = 'DeliveryByCourier'
    DELIVERY_BY_CLIENT = 'DeliveryByClient'