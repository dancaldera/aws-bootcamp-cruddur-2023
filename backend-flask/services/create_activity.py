from datetime import datetime, timedelta, timezone

from lib.db import db


class CreateActivity:
    def run(message, cognito_user_id, ttl):
        model = {
            'errors': None,
            'data': None
        }

        now = datetime.now(timezone.utc).astimezone()

        if (ttl == '30-days'):
            ttl_offset = timedelta(days=30)
        elif (ttl == '7-days'):
            ttl_offset = timedelta(days=7)
        elif (ttl == '3-days'):
            ttl_offset = timedelta(days=3)
        elif (ttl == '1-day'):
            ttl_offset = timedelta(days=1)
        elif (ttl == '12-hours'):
            ttl_offset = timedelta(hours=12)
        elif (ttl == '3-hours'):
            ttl_offset = timedelta(hours=3)
        elif (ttl == '1-hour'):
            ttl_offset = timedelta(hours=1)
        else:
            model['errors'] = ['ttl_blank']

        if message == None or len(message) < 1:
            model['errors'] = ['message_blank']
        elif len(message) > 280:
            model['errors'] = ['message_exceed_max_chars']

        if model['errors']:
            model['data'] = {
                'cognito_user_id':  cognito_user_id,
                'message': message
            }
        else:
            uuid = CreateActivity.create_activity(
                cognito_user_id, message, (now + ttl_offset).isoformat())

            print('uuid123', uuid)

            object_json = CreateActivity.get_activity_by_uuid(uuid)

            model['data'] = object_json
        return model

    def create_activity(cognito_user_id, message, expires_at):
        sql = db.template('activities', 'create')
        val = {'cognito_user_id': cognito_user_id,
               'message': message,
               'expires_at': expires_at}
        uuid = db.query_commit(sql, val)
        return uuid

    def get_activity_by_uuid(uuid):
        sql = db.template('activities', 'get_by_uuid')
        val = {'uuid': uuid}
        activity = db.query_object_json(sql, val)
        return activity
