from __future__ import annotations

import boto3
import psycopg
from psycopg import pq, sql


def create_dsql_connection(
    cluster_identifier: str,
    region,
    client=None,
    cluster_user="admin",
    schema="public",
    expires_in=3600,
):
    cluster_endpoint = f"{cluster_identifier}.dsql.{region}.on.aws"
    if not client:
        client = boto3.client("dsql", region_name=region)

    password_token = client.generate_db_connect_admin_auth_token(
        cluster_endpoint,
        region,
        expires_in,
    )
    conn_params = {
        "dbname": "postgres",
        "user": cluster_user,
        "host": cluster_endpoint,
        "port": "5432",
        "sslmode": "require",
        "password": password_token,
    }

    if pq.version() >= 170000:
        conn_params["sslnegotiation"] = "direct"

    conn = psycopg.connect(**conn_params)
    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SET search_path = {};").format(sql.Identifier(schema)))
    except Exception:
        conn.close()
        raise
    return conn
