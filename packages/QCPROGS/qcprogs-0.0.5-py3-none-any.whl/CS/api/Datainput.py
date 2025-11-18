from dataclasses import asdict, is_dataclass
from typing import Any, Dict
from model import store_information,data_generator,data_vendor,Amount,customer,Timer


class ManagerDataVendor(data_generator):
    def __init__(self,
                 store: store_information = store_information(),
                 data: data_vendor = data_vendor(),
                 amt: Amount = Amount(),
                 cust: customer = customer(),
                 time: Timer = Timer()):
        super().__init__(store=store, data=data, amt=amt, cust=cust, time=time)
        self.value_all: Dict[str, Any] = self.flatten_all()

    def get_store(self) -> store_information:
        return self.store

    def set_store_id(self, value: store_information):
        self.store = value
        self.value_all = self.flatten_all()

    def get_data(self) -> data_vendor:
        return self.data

    def set_data(self, value: data_vendor):
        self.data = value
        self.value_all = self.flatten_all()

    def get_amt(self) -> Amount:
        return self.amt

    def set_amt(self, value: Amount):
        self.amt = value
        self.value_all = self.flatten_all()

    def get_customer(self) -> customer:
        return self.cust

    def set_customer(self, value: customer):
        self.cust = value
        self.value_all = self.flatten_all()

    def get_time(self) -> Timer:
        return self.time

    def set_time(self, value: Timer):
        self.time = value
        self.value_all = self.flatten_all()

    def flatten_all(self) -> Dict[str, Any]:
        combined = {
            **self.flatten_dataclass(self.store),
            **self.flatten_dataclass(self.data),
            **self.flatten_dataclass(self.amt),
            **self.flatten_dataclass(self.cust),
            **self.flatten_dataclass(self.time)
        }
        return combined

    @staticmethod
    def flatten_dataclass(obj: Any) -> Dict[str, Any]:
        """Flatten dataclass เป็น dict แบบ recursive"""
        if not is_dataclass(obj):
            raise ValueError("Input must be a dataclass instance")
        result = {}
        for field_name, value in asdict(obj).items(): # type: ignore
            result[field_name] = value
        return result

    def get_all_item(self) -> Dict[str, Any]:
        return self.value_all
    def __data_refecter_genarater(self):
        ...


if __name__ == '__main__':
    # manager = ManagerDataVendor()
    # print(manager.get_all_item())  # dict เดียวรวมทุก field

    # # อัปเดตค่า store
    # new_store = store_infomation(STORE_ID="12345")
    # manager.set_store_id(new_store)
    # print(manager.get_all_item()["STORE_ID"])  # 12345
    d = data_vendor()
    d.DATA_1 = 7
    print(d.DATA_1)
    # {'input': 7, 'Type': 'int', 'value': '1521545'}

    d.DATA_1 = "2111321321321"
    print(d.DATA_1)
    # {'input': 'Hello', 'Type': 'str', 'value': 'Hello'}

    d.DATA_1 = ['12121212', 20, 30]
    print(d.DATA_1)
    # {'input': [10, 20, 30], 'Type': 'list', 'value': 10}


