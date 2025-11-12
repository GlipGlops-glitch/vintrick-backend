import os
import sys
import pyodbc
from dotenv import load_dotenv


def escape_odbc_value(val: str) -> str:
    """
    Safely escape ODBC connection string values.
    Wrap in braces if the value contains ; or braces, and escape closing braces.
    """
    s = str(val)
    if any(ch in s for ch in [';', '{', '}']):
        s = s.replace('}', '}}')
        return '{' + s + '}'
    return s


def build_conn_str() -> str:
    server = os.getenv("DB_LIMS_SERVER")
    database = os.getenv("DB_LIMS_DATABASE")
    driver = os.getenv("DB_LIMS_DRIVER", "ODBC Driver 18 for SQL Server")
    encrypt = os.getenv("DB_LIMS_ENCRYPT", "yes")
    trust_cert = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    user = os.getenv("DB_LIMS_USER") or ""
    password = os.getenv("DB_LIMS_PASSWORD") or ""

    missing = [k for k, v in {
        "DB_LIMS_SERVER": server,
        "DB_LIMS_DATABASE": database,
    }.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"Encrypt={encrypt}",
        f"TrustServerCertificate={trust_cert}",
    ]

    # Use SQL Authentication if both user and password are supplied; otherwise use Windows Authentication
    if user and password:
        parts.append(f"UID={escape_odbc_value(user)}")
        parts.append(f"PWD={escape_odbc_value(password)}")
        parts.append("Trusted_Connection=no")
    else:
        parts.append("Trusted_Connection=yes")

    return ";".join(parts)


def main():
    load_dotenv()  # Load variables from .env

    schema = os.getenv("DB_LIMS_SCHEMA", "dbo")
    table = os.getenv("DB_LIMS_TABLE", "Samples")

    conn_string = build_conn_str()
    sql = f"SELECT TOP 50 * FROM [{schema}].[{table}]"

    try:
        with pyodbc.connect(conn_string, timeout=30) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                columns = [d[0] for d in cur.description]
                rows = cur.fetchall()
    except pyodbc.Error as e:
        print("Database error:", e, file=sys.stderr)
        sys.exit(1)

    # Print header
    print("\t".join(columns))
    # Print rows
    for row in rows:
        print("\t".join("" if v is None else str(v) for v in row))


if __name__ == "__main__":
    main()