from psycopg_pool import ConnectionPool
import sys
import os


class Database:
    def __init__(self):
        self.connection_url = os.getenv("CONNECTION_URL")
        self.pool = ConnectionPool(self.connection_url)

    def query_wrap_object(self, template):
        sql = f"""
        (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
        {template}
        ) object_row);
        """
        return sql

    def query_wrap_array(self, template):
        sql = f"""
        (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
        {template}
        ) array_row);
        """
        return sql

    def query_commit(self, sql, val):
        try:
            conn = self.pool.getconn()
            cur = conn.cursor()
            cur.execute(sql, val)
            conn.commit()
            cur.close()
            self.pool.putconn(conn)
        except Exception as err:
            self.print_psycopg_err(err)
            return False
        return True

    def query_array_json(self, sql):
        try:
            wrapped_sql = self.query_wrap_array(sql)
            conn = self.pool.getconn()
            cur = conn.cursor()
            cur.execute(wrapped_sql)
            json = cur.fetchone()
            cur.close()
            self.pool.putconn(conn)
        except Exception as err:
            self.print_psycopg_err(err)
            return False
        return json[0]

    def query_object_json(self, sql):
        try:
            wrapped_sql = self.query_wrap_object(sql)
            conn = self.pool.getconn()
            cur = conn.cursor()
            cur.execute(wrapped_sql)
            json = cur.fetchone()
            cur.close()
            self.pool.putconn(conn)
        except Exception as err:
            self.print_psycopg_err(err)
            return False
        return json[0]

    def print_psycopg_err(self, err):
        err_type, err_obj, traceback = sys.exc_info()

        line_num = traceback.tb_lineno

        print(f"""
            PSYCOPG ERROR:
            {err_type}
            {err_obj}
            LINE NUMBER: {line_num}
            """)

        print(f"""
            extention: {err}
            """)

        print(f"""
            pgcode: {err.pgcode}
            pgerror: {err.pgerror}
            """)
