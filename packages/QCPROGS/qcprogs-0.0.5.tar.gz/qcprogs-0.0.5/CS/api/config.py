from enum import Enum


class ActionCode(Enum):
    INQUIRY = (0,'Inquiry')
    DATAEXCHANGE = (1,'DataExchange')
    
    DATAEXCHANGECONFIRM=(3,'DataExchangeConfirm')
    REPRINTSLIP = (3,'REPRINTSLIP')
    CANCEL = (5,'Cancel')
    OR = (6,'OR')
    ORCANCEL = (5,'ORCancel')
    ORCONFIRM = (9,'ORConfirm')

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.code} {self.message}"

    def as_dict(self):
        return {"code": str(self.code), "message": self.message}

    @classmethod
    def from_code(cls, code: int):
        for status in cls:
            if status.code == code:
                return status
        raise ValueError(f"No ActionCode found for code: {code}")
    


  
# class xmlconfig(Enum):
#     xmlencoder='<?xml version="1.0" encoding="UTF-8"?>'

# BELIEVABLE = {"HQ_REQUEST":
#             [{"SERVICE_BOX":
#               [{"ADDRESS":
#                 ['VENDOR_ID','SERVICE_ID','METHOD'],
#                 "DATA":
#                 ['PAYMENT_CHANNEL','VENDOR_ID','SERVICE_ID','SERV_ID','STATION_ID',
#                  'BUS_DATE','BUS_TIME','SYS_DATE','SYS_TIME','COMMON_TRN_ID','TX_ID',
#                  'SEQ_NO','STORE_ID','CLIENT_SERV_SEQ','SHIFT_ID',"TRANS_TYPE",'BILL_AMT',
#                  'PAYMENT_TYPE','CANCEL_ID','ROUND_BILL_AMT','VAT_AMT','ACCT_NO','EMPLOYEE_ID',
#                  'REPT_TYPE','REPT_NO','PREV_REF_SEQ','PREV_REF_DATE','SERV_CHARGE_NO','ITEM_NAME',
#                  'ITEM_SELECTION','POS_TAX_ID','ZONE','DATA_1','DATA_2','DATA_3','DATA_4','DATA_5',
#                  'DATA_6','DATA_7','DATA_9','TOT_BILL_TRANS','CUST_NAME','CUST_ADDR_1','CUST_ADDR_2',
#                  'CUST_ADDR_3','CUST_PHONE_NO'
#                  ]}]}]}
