from datetime import datetime, timedelta, timezone

from lib.db import db


class HomeActivities:
    def run(cognito_user_id=None):
        sql = db.template('activities', 'get_all')

        results = db.query_array_json(sql)

        return results
