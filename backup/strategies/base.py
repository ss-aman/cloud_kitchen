from abc import ABC, abstractmethod

class BackupStrategy(ABC):
    @abstractmethod
    def backup(self, data, backup_name):
        pass
    
    @abstractmethod
    def restore(self, backup_name):
        pass
    
    @abstractmethod
    def list_backups(self):
        pass
