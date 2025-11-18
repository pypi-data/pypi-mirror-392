from dataclasses import dataclass, field,fields
from datetime import datetime
from random import randint,choice
from typing import Optional,Any,List
from  config import  ActionCode


@dataclass
class store_information:
    STORE_ID: str = "09892"
    VENDOR_ID: str = "82204"
    SERVICE_ID: str = "00"
    VENDOR_NAME: str = "Test"
    ZONE: str = choice(["1","2"])
    EMPLOYEE_ID: str = "0555505"
    POS_TAX_ID: str = ''.join([str(randint(0,9)) for i in range(13)])
    VAT_AMT: str = "0"
    REPT_TYPE: str = "H"
    PAYMENT_CHANNEL: str = "C05"    
    STEP: int = 1  
@dataclass  
class data_vendor:
    DATA_1: Any = field(default=None)
    DATA_2: Any = field(default=None)
    DATA_3: Any = field(default=None)
    DATA_4: Any = field(default=None)
    DATA_5: Any = field(default=None)
    DATA_6: Any = field(default=None)
    DATA_7: Any = field(default=None)
    DATA_9: Any = field(default=None)

    def __setattr__(self, name: str, value: Any):
        """Intercept assignment to auto-type-check and structure value"""
        if name.startswith("_"):  # allow internal attributes
            super().__setattr__(name, value)
            return

        data_dict = self._format_value(value)
        super().__setattr__(name, data_dict)

    @staticmethod
    def _format_value(value: Any) -> dict:
        if value is None:
            return {"input": None, "Type": "NoneType", "value": ""}

        if isinstance(value, int):
            return {"input": value, "Type": "int", "value":''.join([str(randint(0,9)) for _ in range(int(value))])}

        if isinstance(value, float):
            return {"input": value, "Type": "float", "value": f"{value:.2f}"}

        if isinstance(value, str):
            return {"input": value, "Type": "str", "value": value}

        if isinstance(value, list):
            val = value[0] if value else ""
            return {"input": value, "Type": "list", "value": val}

        return {"input": value, "Type": type(value).__name__, "value": str(value)}


@dataclass  
class Amount:
    Placeholder :Optional[str] = ""
    amountdefect: Optional[str] | float = 50.00
    MinAmount : Optional[str]|float = 1.00
    MaxAmount : Optional[str]|float = 90000.00
    BelowMinAmount :Optional[str]|float=MinAmount-0.01
    AboveMaxAmount : Optional[str]|float = MaxAmount+0.01
    AmountRound : Optional[str]|float = amountdefect + choice([i / 100 for i in range(1, 100) if (i * 4) % 100 == 0])
    AmountNonRound : Optional[str]|float = amountdefect + choice([i / 100 for i in range(1, 100) if (i * 4) % 100 != 0])
    amountedit : Optional[str] | float = amountdefect + choice([i for i in range(1, 100, choice([3, 7, 9, 11]))])
@dataclass  
class customer:
    CUST_NAME: str = ""
    CUST_ADDR_1: str = ""
    CUST_ADDR_2: str = ""
    CUST_ADDR_3: str = ""
    CUST_PHONE_NO: str = ""
@dataclass  
class Timer:
    Minutes: str = "0"
    Hours: str = "0"
    MinuteNew: str = "0"
    HoursNew: str = "0"
    Date: str = field(default_factory=lambda: datetime.now().strftime("%Y/%m/%d"))
    Time: str = field(default_factory=lambda: datetime.now().strftime("%X"))
    Random_Num: str = field(default_factory=lambda: str(randint(0, 100)))

@dataclass
class data_generator:
    store:store_information
    data:data_vendor
    amt:Amount
    cust:customer
    time:Timer


@dataclass
class Address:
    VENDOR_ID: str
    SERVICE_ID: str
    METHOD: ActionCode = ActionCode.DATAEXCHANGE

    def method_code(self) -> int:
        return self.METHOD.code

    def method_message(self) -> str:
        return self.METHOD.message


@dataclass
class Data:
    PAYMENT_CHANNEL: Optional[int] = None
    VENDOR_ID: Optional[str] = None
    SERVICE_ID: Optional[str] = None
    SERV_ID: Optional[str] = None
    STATION_ID: Optional[str] = None
    BUS_DATE: Optional[str] = None
    BUS_TIME: Optional[str] = None
    SYS_DATE: Optional[str] = None
    SYS_TIME: Optional[str] = None
    COMMON_TRN_ID: Optional[str] = None
    TX_ID: Optional[str] = None
    SEQ_NO: Optional[str] = None
    STORE_ID: Optional[str] = None
    CLIENT_SERV_SEQ: Optional[str] = None
    SHIFT_ID: Optional[str] = None
    TRANS_TYPE: Optional[str] = None
    BILL_AMT: Optional[float] = None
    PAYMENT_TYPE: Optional[str] = None
    CANCEL_ID: Optional[str] = None
    ROUND_BILL_AMT: Optional[float] = None
    VAT_AMT: Optional[float] = None
    ACCT_NO: Optional[str] = None
    EMPLOYEE_ID: Optional[str] = None
    REPT_TYPE: Optional[str] = None
    REPT_NO: Optional[str] = None
    PREV_REF_SEQ: Optional[str] = None
    PREV_REF_DATE: Optional[str] = None
    SERV_CHARGE_NO: Optional[str] = None
    ITEM_NAME: Optional[str] = None
    ITEM_SELECTION: Optional[str] = None
    POS_TAX_ID: Optional[str] = None
    ZONE: Optional[str] = None
    DATA_1: Optional[str] = None
    DATA_2: Optional[str] = None
    DATA_3: Optional[str] = None
    DATA_4: Optional[str] = None
    DATA_5: Optional[str] = None
    DATA_6: Optional[str] = None
    DATA_7: Optional[str] = None
    DATA_9: Optional[str] = None
    TOT_BILL_TRANS: Optional[float] = None
    CUST_NAME: Optional[str] = None
    CUST_ADDR_1: Optional[str] = None
    CUST_ADDR_2: Optional[str] = None
    CUST_ADDR_3: Optional[str] = None
    CUST_PHONE_NO: Optional[str] = None


@dataclass
class ServiceBox:
    ADDRESS: Address
    DATA: Data


@dataclass
class HQRequest:
    SERVICE_BOX: List[ServiceBox] = field(default_factory=list)





def extract_data_vendor_values(dv: data_vendor) -> dict:
    result = {}
    for f in fields(dv):
        val = getattr(dv, f.name)
        # ถ้าเป็น dict แบบ _format_value
        if isinstance(val, dict) and "value" in val:
            result[f.name] = val["value"]
        else:
            result[f.name] = val
    return result