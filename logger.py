from database.database import get_connection


def log(

    username,

    action,

    severity="INFO"

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO audit_logs(

        username,

        action,

        severity

    )

    VALUES(?,?,?)

    """,(

        username,

        action,

        severity

    ))

    conn.commit()

    conn.close()