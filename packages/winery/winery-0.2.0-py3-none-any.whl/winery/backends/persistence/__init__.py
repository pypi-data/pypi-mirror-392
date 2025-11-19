from ...contracts import PersistenceContract

MARIA_SQL_TABLES = [
    """CREATE TABLE IF NOT EXISTS template_types(
        `template_type` VARCHAR(2) PRIMARY KEY,
        `description` VARCHAR(32) UNIQUE KEY,
        
        `date_added` DATETIME DEFAULT CURRENT_TIMESTAMP());
        """,
    """CREATE TABLE IF NOT EXISTS templates(
        `template_id` VARCHAR(36) PRIMARY KEY,
        `name` VARCHAR(16) UNIQUE KEY,
        `template_type` VARCHAR(2) NOT NULL,
        `date_added` DATETIME DEFAULT CURRENT_TIMESTAMP(),
        `date_updated` DATETIME DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
        
        CONSTRAINT fk_template_type FOREIGN KEY (template_type) REFERENCES template_types(template_type)
            ON DELETE RESTRICT
            ON UPDATE CASCADE
        
        ); """,
        """INSERT INTO template_types(template_type, description)
        VALUES("S", "System templates")
        """
]
