import pytest
from winery.backends.persistence.mariadb import MariaBackend


@pytest.fixture
def backend(winery_instance, mariadb_service, tmp_path):
    """
    Provides a configured MariaBackend instance connected to the test container.
    """
    # Create a winery instance configured to use the MariaDB container
    winery = winery_instance(
        template_path=tmp_path,
        local_time="UTC",
        persistant_backend=MariaBackend,
        database_user=mariadb_service["user"],
        database_password=mariadb_service["password"],
        database_host=mariadb_service["host"],
        database_name=mariadb_service["database"],
        database_port=mariadb_service["port"],
    )
    return winery.persistant_backend


def test_get_db(backend):
    """
    Tests the get_db context manager to ensure it provides a functional cursor.
    """
    with backend.get_db() as cur:
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        assert result == (1,)


def test_create_tables(backend):
    """
    Tests that the create_tables method successfully creates the defined tables.
    """
    backend.create_tables()

    with backend.get_db() as cur:
        cur.execute("SHOW TABLES;")
        tables = {row[0] for row in cur.fetchall()}
        assert "templates" in tables
        assert "template_types" in tables