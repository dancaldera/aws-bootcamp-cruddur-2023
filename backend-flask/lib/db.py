from psycopg_pool import ConnectionPool
import sys
import os
import re
from flask import current_app as app


class Database:
    def __init__(self):
        self.connection_url = os.getenv("CONNECTION_URL")
        self.pool = ConnectionPool(self.connection_url)

    def template(self, *args):
        pathing = list((app.root_path, 'db', 'sql',) + args)
        pathing[-1] = pathing[-1] + '.sql'

        green = '\033[32m'
        no_color = '\033[0m'
        template_path = os.path.join(*pathing)

        print(f"{green}Loading template from {template_path}{no_color}")
        with open(template_path, 'r') as f:
            sql = f.read()
        return sql

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

    def print_params(self, params):
        blue = '\033[94m'
        no_color = '\033[0m'
        print(f'{blue} SQL Params:{no_color}')
        for key, value in params.items():
            print(key, ":", value)

    def print_sql(self, title, sql, params={}):
        cyan = '\033[96m'
        no_color = '\033[0m'
        print(f'{cyan} SQL STATEMENT-[{title}]------{no_color}')
        print(sql, params)

    def query_commit(self, sql, val):
        is_returning = sql.find('RETURNING') > -1

        if is_returning:
            return self.query_commit_with_returning_uuid(sql, val)

        self.print_sql('', sql)

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

    def query_commit_with_returning_uuid(self, sql, val):
        self.print_sql('with returning uuid', sql)
        try:
            conn = self.pool.getconn()
            cur = conn.cursor()
            cur.execute(sql, val)
            uuid = cur.fetchone()
            conn.commit()
            cur.close()
            self.pool.putconn(conn)
        except Exception as err:
            self.print_psycopg_err(err)
            return False
        return uuid[0]

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

   # When we want to return an array of json objects
    def query_object_json(self, sql, params={}):

        self.print_sql('json', sql)
        self.print_params(params)
        wrapped_sql = self.query_wrap_object(sql)

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql, params)
                json = cur.fetchone()
                if json == None:
                    "{}"
                else:
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


db = Database()
