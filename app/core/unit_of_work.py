from sqlmodel import Session


# Esta clase solo expone los metodos de commit y rollback de Session
# La usamos en la capa de servicios para no recibir directamente ningun objeto diracto de bd, es una abstraccion
# Se usa en los servicios que necesitan llamar directamente a commit o rollback
class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, instance: object):
        self.db.refresh(instance)

    def flush(self):
        self.db.flush()
