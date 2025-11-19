import pytest
import tempfile
import time
import docker
import mariadb
from winery import Winery
from winery.utils.dateutils import DateHelper
from winery.backends.persistence.mariadb import MariaBackend

@pytest.fixture
def winery_instance():
    yield Winery


@pytest.fixture
def conf():
    return {"local_time": "Europe/London"}


@pytest.fixture
def winery_config(conf):
    with tempfile.TemporaryDirectory as tempdir:
        return Winery(template_path=tempdir, local_time=conf["local_time"])


@pytest.fixture
def date_helper():
    yield DateHelper


@pytest.fixture(scope="session")
def mariadb_service():
    """
    Spins up a MariaDB container for integration testing.
    This fixture has session scope to avoid restarting the container for every test.
    """
    client = docker.from_env()
    container_name = "winery-test-mariadb"
    db_config = {
        "user": "winery",
        "password": "testpassword",
        "database": "winery_db",
    }

    # Ensure no old container with the same name is running
    try:
        old_container = client.containers.get(container_name)
        old_container.remove(force=True)
    except docker.errors.NotFound:
        pass

    container = client.containers.run(
        "mariadb:latest",
        name=container_name,
        environment={
            "MARIADB_ROOT_PASSWORD": "rootpassword",
            "MARIADB_USER": db_config["user"],
            "MARIADB_PASSWORD": db_config["password"],
            "MARIADB_DATABASE": db_config["database"],
        },
        ports={"3306/tcp": None},  # Let Docker assign a random host port
        detach=True,
    )

    # Wait for the container to assign a port
    host_port = None
    for _ in range(10):  # Wait up to 10 seconds
        container.reload()
        if container.ports.get("3306/tcp"):
            host_port = container.ports["3306/tcp"][0]["HostPort"]
            break
        time.sleep(1)
    db_config["host"] = "127.0.0.1"
    db_config["port"] = int(host_port)

    # Wait for the database to be ready
    for _ in range(20):  # Wait up to 20 seconds
        try:
            mariadb.connect(**db_config)
            break
        except mariadb.Error:
            time.sleep(1)

    yield db_config

    # Teardown: stop and remove the container
    container.remove(force=True)
