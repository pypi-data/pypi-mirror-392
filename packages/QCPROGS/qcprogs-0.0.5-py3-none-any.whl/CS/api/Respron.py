import requests
import base64
from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom
from icecream import ic
def dict_to_xml(d: dict, root_key='HQ_REQUEST') -> str:
    def build_xml_element(parent, data):
        for key, value in data.items():
            elem = Element(key)
            
            if isinstance(value, dict):
                # recursive สำหรับ dict
                build_xml_element(elem, value)
            elif isinstance(value, list):
                if all(isinstance(v, dict) for v in value):
                    # ถ้า list เป็น dict ให้วน for แต่ละ dict
                    for v in value:
                        build_xml_element(elem, v)
                else:
                    # ถ้าเป็น str/int/float ให้รวมด้วย |
                    elem.text = '|'.join(str(v) for v in value)
            else:
                # str/int/float
                elem.text = str(value if value is not None else '')
            parent.append(elem)
    root = Element(root_key)
    build_xml_element(root,d) # type: ignore
    
    # ทำให้ XML อ่านง่าย
    xml_str = tostring(root, encoding='utf-8').decode("utf-8")
    # pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    return f'<?xml version="1.0" encoding="UTF-8"?>{xml_str}'

def call_service_xml(url: str, data: str) -> str:
    def build_soap_request(value_xml: str,service_name: str|None ='CSService', ) -> str:
        """
        สร้าง SOAP XML Envelope สำหรับส่ง SOAP Request
        Args:
            service_name (str): ชื่อ service เช่น "CSService"
            value_xml (str): XML ภายในที่ต้องการส่ง (จะถูกห่อใน CDATA)
        Returns:
            str: SOAP XML พร้อมใช้งาน
        """

        URLSCHEMA = 'http://schemas.xmlsoap.org/soap/envelope/'
        URLPOR = 'http://portal.cs/'
        SOAPENV = f'xmlns:soapenv="{URLSCHEMA}"'
        STLPOR = f'xmlns:por="{URLPOR}"'
        SOAPHEADER = f'<soapenv:Envelope {SOAPENV} {STLPOR}><soapenv:Header/>'
        data_cdata = f'<![CDATA[{value_xml}]]>'
        arg = f'<arg0>{data_cdata}</arg0>'
        optional = '<!--Optional:-->'
        por_block = f'<por:{service_name}>{optional}{arg}</por:{service_name}>'
        soap_body = f'<soapenv:Body>{por_block}</soapenv:Body>'
        soap_xml = f'{SOAPHEADER}{soap_body}</soapenv:Envelope>'
        return soap_xml

    try:
        # response = requests.request("POST",url=url, headers={'Content-Type': 'text/xml'}, data=data,timeout=15)
        data = build_soap_request(data)
        ic(data)
        response = requests.post(
            url=url,
            headers={'Content-Type': 'text/xml'},
            data=data,
            timeout=15
        )
        response.raise_for_status()

        text = response.text
        start = text.find("<return>")
        end = text.find("</return>")

        if start == -1 or end == -1:
            raise ValueError("Tag <return> not found in response")

        encoded_str = text[start + 8:end].strip()
        decoded_str = base64.b64decode(encoded_str).decode('utf-8')

        return decoded_str

    except Exception as e:
        return f"Error processing response: {e}"