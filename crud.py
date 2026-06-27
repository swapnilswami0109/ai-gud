from database.database import get_connection


def add_project(
    name,
    description,
    owner
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO projects(

        name,

        description,

        owner

    )

    VALUES(?,?,?)

    """,(

        name,

        description,

        owner

    ))

    conn.commit()

    conn.close()


def get_projects():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT * FROM projects

    ORDER BY id DESC

    """)

    data = cursor.fetchall()

    conn.close()

    return data