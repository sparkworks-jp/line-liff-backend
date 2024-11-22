from enum import IntEnum

class OrderStatus(IntEnum):
    CREATED = 1
    PENDING_PAYMENT = 2
    PAID = 3
    SHIPPED = 4
    COMPLETED = 5
    CANCELED = 6

    @classmethod
    def choices(cls):
        return [(status.value, status.name.capitalize()) for status in cls]