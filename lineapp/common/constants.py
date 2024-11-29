from enum import IntEnum


class OrderStatus(IntEnum):
    PENDING_PAYMENT = 1
    PAID = 2
    SHIPPED = 3
    COMPLETED = 4
    CANCELED = 5

    @classmethod
    def choices(cls):
        return [(status.value, status.name.capitalize()) for status in cls]


class SaleStatus(IntEnum):
    ON_SALE = 1  # 販売中
    STOP_SALE = 2  # 販売停止

