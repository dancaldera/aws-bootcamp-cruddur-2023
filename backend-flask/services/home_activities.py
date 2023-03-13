from datetime import datetime, timedelta, timezone

from lib.db import Database


class HomeActivities:
    def run(cognito_user_id=None):
        db = Database()
        results = db.query_array_json("""
        SELECT
            activities.uuid,
            users.display_name,
            users.handle,
            activities.message,
            activities.replies_count,
            activities.reposts_count,
            activities.likes_count,
            activities.reply_to_activity_uuid,
            activities.expires_at,
            activities.created_at
        FROM public.activities
        LEFT JOIN public.users ON users.uuid = activities.user_uuid
        ORDER BY activities.created_at DESC
        """)

        return results
