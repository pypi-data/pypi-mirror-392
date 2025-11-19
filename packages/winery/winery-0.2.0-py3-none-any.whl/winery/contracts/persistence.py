from abc import ABC, abstractmethod


class PersistenceContract(ABC):
    def __init__(self, winery):
        self.winery = winery

    @abstractmethod
    def add_template(self, template_name):
        pass

    @abstractmethod
    def get_template(self, template_name):
        pass

    @abstractmethod
    def update_template(self, template_name, new_content):
        pass

    @abstractmethod
    def delete_template(self, template_name):
        pass

    @abstractmethod
    def list_templates(self):
        pass
