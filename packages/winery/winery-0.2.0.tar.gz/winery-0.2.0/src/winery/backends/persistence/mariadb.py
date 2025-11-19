from . import PersistenceContract
import mariadb
from . import MARIA_SQL_TABLES
from contextlib import contextmanager
class MariaBackend(PersistenceContract):
    
    def __init__(self, winery):
        self.winery = winery
        super().__init__(winery)
        
        
        
    def connect(self):
        connection_dict = {
            "user": self.winery.database_user,
            "password": self.winery.database_password,
            "host": self.winery.database_host,
            "database": self.winery.database_name,
            "port": self.winery.database_port,
        }
        return mariadb.connect(**connection_dict)
    
    @contextmanager
    def get_db(self):
        conn = self.connect()
        cur = conn.cursor()
        conn.begin()
        yield cur
        cur.close()
        conn.commit()
        conn.close()
        
    def create_tables(self):
        for table in MARIA_SQL_TABLES:
            with self.get_db() as cur:
                cur.execute(table)

    def add_template(self, template_name):
        raise NotImplementedError


    def get_template(self, template_name):
        raise NotImplementedError

    def update_template(self, template_name, new_content):
        raise NotImplementedError

    def delete_template(self, template_name):
        raise NotImplementedError

    def list_templates(self):
        raise NotImplementedError
