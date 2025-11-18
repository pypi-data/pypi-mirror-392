from oracledb import makedsn,connect
from icecream import ic
from typing import List, Any



class ConnetDatabase:
    host = '10.182.236.52'
    port = 1521
    service_name='ONLPRD'
    user = 'cs_support'
    user_admin='cs_dev'
    password = '1234'
    def __init__(self, host: str | None=None):
        if host:
            self.host= host
        self.__connect()
    def __connect(self):
        try:
            self.conn = connect(
                user=self.user,
                password=self.password, 
                dsn=makedsn(
                    host=self.host,
                    port=self.port,
                    service_name=self.service_name
                    )
                ) 
            ic("Connected to Oracle Database")
        except Exception as e:
            ic("Connection failed:", e)
    @staticmethod
    def __formater_rows(rows: List[List[Any]]) -> List[List[str]]:
        cleaned_data = []
        for row in rows:
            cleaned_row = []
            for v in row:
                if v is None:
                    cleaned_row.append("")
                else:
                    s = str(v).replace("\n", " ").replace("\r", " ").strip()
                    try:
                        s = s.encode('latin1').decode('tis-620', errors='ignore')
                    except Exception as e:
                        ic("Connection failed:", e)
                        s = s
                    cleaned_row.append(s)
            cleaned_data.append(cleaned_row)
        return cleaned_data
    def _run_query(self, query, fetch=True):
        with self.conn.cursor() as cur:
            cur.execute(query)
            if fetch:
                cols = [c[0] for c in cur.description] # pyright: ignore[reportOptionalIterable]
                rows = cur.fetchall()
                rows_clean = self.__formater_rows(rows)
            
        return {'Column':cols,'rows':rows_clean}
    # ---------------- Query Templates ----------------
    def client_config(self, vendor: str, service: str):
        sql = f"""
        SELECT * FROM (
            SELECT dg.VENDOR_ID, dg.SERVICE_ID, dg.SYSTEM_TYPE, dg.MIN_AMT,
                   dg.MAX_AMT, dg.OR_TIMEOUT, dg.SERVICE_CHARGE, dg.VENDOR_NAME,
                   dg.LOG_ID, df.SERVER_RUN
            FROM ONLSTD.WS_CLIENT_AUTOFIXTX df
            RIGHT JOIN ONLSTD.WS_CLIENT_CONFIG dg
                   ON df.VENDOR_ID = dg.VENDOR_ID
                  AND df.SERVICE_ID = dg.SERVICE_ID
            ORDER BY dg.EXPIRE_DATE DESC
        )
        WHERE VENDOR_ID = '{vendor}' AND SERVICE_ID = '{service}'
        """
        return self._run_query(sql)

    def charge_step(self, vendor: str, service: str):
        sql = f"""
        SELECT VENDOR_ID, SERVICE_ID, MIN_AMOUNT, MAX_AMOUNT,
               SERVICE_CHARGE_CENTRE, SERVICE_CHARGE_PROVINCES
        FROM ONLSTD.WS_CLIENT_CHARGE_STEP
        WHERE VENDOR_ID = '{vendor}' AND SERVICE_ID = '{service}'
        """
        return self._run_query(sql)

    def update_or_timeout(self, vendor: str, service: str, timeout: int):
        sql = f"""
        UPDATE ONLSTD.WS_CLIENT_CONFIG
        SET OR_TIMEOUT = '{timeout}'
        WHERE VENDOR_ID = '{vendor}'
          AND SERVICE_ID = '{service}'
          AND EFF_DATE <= CURRENT_DATE
          AND EXPIRE_DATE >= CURRENT_DATE
        """
        return self._run_query(sql, fetch=False)

    def online_tx(self, *txids: str):
        if not txids:
            return [] 
        placeholders = ", ".join([f":p{i}" for i in range(len(txids))])
        sql = f"""
            SELECT *
            FROM ONLSTD.WS_ONLINE_TX
            WHERE TX_ID IN ({placeholders})
            OR R_SERVICE_RUNNO IN ({placeholders})
        """
        params = {f"p{i}": v for i, v in enumerate(txids)}

        return self._run_query(sql, params) # type: ignore



