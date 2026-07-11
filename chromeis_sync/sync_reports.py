import frappe
import pymysql

def test_db_connection():
    try:
        conn = pymysql.connect(
            host='chromeis.com',
            user='chrom_erpnxt',
            password='95$2}ZnMNr.',
            database='chrom_restore_WHMCS',
            connect_timeout=5
        )
        print("SUCCESS: Connection established!")
        conn.close()
    except Exception as e:
        print(f"FAILED: {e}")
