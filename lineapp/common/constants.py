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

regions = {
    "HOKKAIDO": range(0, 10),
    "TOUHOKU": range(10, 40),
    "KANTO": range(100, 300),
    "CHUBU": range(300, 500),    
    "KINKI": range(500, 680),     
    "CHUUGOKU": range(680, 700),  
    "SHIKOKU": range(700, 800), 
    "KYUSHU": range(800, 900),     
    "OKINAWA": range(900, 1000)  
}


shipping_fees = {
    "HOKKAIDO": 2000,
    "TOUHOKU": 1500,
    "KANTO": 1200,
    "CHUBU": 1500,
    "KINKI": 1500,
    "CHUUGOKU": 1800,
    "SHIKOKU": 1800,
    "KYUSHU": 1800,
    "OKINAWA": 2300,
}