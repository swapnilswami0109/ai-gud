import hashlib

from database.database import get_connection


def encrypt(password):

    return hashlib.sha256(

        password.encode()

    ).hexdigest()


def register(

    full_name,

    email,

    password

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO users(

        full_name,

        email,

        password

    )

    VALUES(?,?,?)

    """,(

        full_name,

        email,

        encrypt(password)

    ))

    conn.commit()

    conn.close()


def login(

    email,

    password

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM users

    WHERE email=?

    AND password=?

    """,(

        email,

        encrypt(password)

    ))

    user = cursor.fetchone()

    conn.close()

    return user