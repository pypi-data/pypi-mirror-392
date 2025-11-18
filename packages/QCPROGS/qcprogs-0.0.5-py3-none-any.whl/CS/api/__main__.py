# noinspection PyUnresolvedRefere
from dataclasses import dataclass, asdict, is_dataclass,fields,field
import sys, os
sys.path.append(os.path.dirname(__file__))
from icecream import ic
from typing import Any, Dict,List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from model import data_generator,extract_data_vendor_values,store_information,data_vendor,customer,Timer,Amount
from config import ActionCode
from Respron import call_service_xml
from Datainput import ManagerDataVendor


@dataclass
class Address:
    STREET: str = "Test Street"
    CITY: str = "Bangkok"

@dataclass
class ServiceBox:
    ADDRESS: Address
    DATA: data_vendor  # ใช้ data_vendor ของคุณ

@dataclass
class HQRequest:
    SERVICE_BOX: List[ServiceBox] = field(default_factory=list)


class TransactionManager:
    call_service: Dict[str, Any] = call_service_xml
    def __init__(self, url: str, data_gen: data_generator, config =HQRequest):
        self.url = url
        self.data_gen = data_gen
        self.config = config()
        self.flattened: Dict[str, Any] = self._flatten_data()

    # flatten dataclass เป็น dict เดียว
    def _flatten_data(self):
        result = {}
        if not is_dataclass(self.data_gen):
            raise TypeError("data_gen ต้องเป็น dataclass instance")

        for f in fields(self.data_gen):
            value = getattr(self.data_gen, f.name)
            if is_dataclass(value):
                # ตรวจสอบว่าเป็น data_vendor
                if isinstance(value, data_vendor):
                    result.update(extract_data_vendor_values(value))
                else:
                    result.update(asdict(value))
            elif isinstance(value, dict):
                result.update(value)
            else:
                result[f.name] = value

        return result

    @staticmethod
    def hq_request_to_xml(hq_request: HQRequest) -> str:
        """
        แปลง HQRequest dataclass เป็น XML string
        """
        def create_element(parent,
                           name,
                           value_str):
            if value_str is None:
                value_str = ""
            child = SubElement(parent, name)
            child.text = str(value_str)
            return child

        root = Element("HQ_REQUEST")

        for service_box in hq_request.SERVICE_BOX:
            sb_elem = SubElement(root, "SERVICE_BOX")

            # ADDRESS
            address_elem = SubElement(sb_elem, "ADDRESS")
            data_elem = SubElement(sb_elem, "DATA")
            for field_name, val_dict in vars(service_box.DATA).items():
                # val_dict เป็น dict จาก _format_value
                if isinstance(val_dict, dict) and "value" in val_dict:
                    create_element(data_elem, field_name, val_dict["value"])
                else:
                    create_element(data_elem, field_name, val_dict)

            # DATA
            data_elem = SubElement(sb_elem, "DATA")
            for field_name, value in vars(service_box.DATA).items():
                create_element(data_elem, field_name, value)

        # ทำให้ XML สวยงาม
        xml_str = tostring(root, encoding='utf-8')
        parsed = minidom.parseString(xml_str)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding='UTF-8')
        ic(pretty_xml)
        return pretty_xml.decode('utf-8')
    def _generate_xml(self) -> str:
        xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<HQ_REQUEST>', '<SERVICE_BOX>']
        for k, v in self.flattened.items():
            xml_parts.append(f"<{k}>{v}</{k}>")
        xml_parts.extend(['</SERVICE_BOX>', '</HQ_REQUEST>'])
        return '\n'.join(xml_parts)

    # --- Public method --- ผู้ใช้เรียกใช้งานง่าย ๆ
    def run(self) -> str:
        """
        ทำทุกขั้นตอน: flatten data → สร้าง XML → ส่ง request → decode response
        """



        xml_data: str = self.hq_request_to_xml(self.config)
        ic(xml_data)
        decoded_response = call_service_xml(self.url,xml_data)
        ic(decoded_response)
        return decoded_response
if __name__ == '__main__':
    d = data_vendor()
    d.DATA_1 = 7

    # สร้าง ServiceBox + HQRequest
    sb = ServiceBox(ADDRESS=Address(), DATA=d)
    hq_instance = HQRequest(SERVICE_BOX=[sb])

    # สร้าง data_generator ตัวอย่าง
    dg = data_generator(
        store=store_information(),
        data=d,
        amt=Amount(),
        cust=customer(),
        time=Timer()
    )

    # เรียก TransactionManager
    tm = TransactionManager('localhost', dg, lambda: hq_instance)  # ใช้ lambda เพื่อส่ง instance
    tm.run()