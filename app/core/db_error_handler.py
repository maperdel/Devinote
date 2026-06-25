from contextlib import contextmanager
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import DatabaseOperationError, IntegrityErrorExc
from app.core.unit_of_work import UnitOfWork


# Crea un context manager que encapsula las operaciones de bd en el servicio que pudieran lanzar un error
@contextmanager
def handle_db_errors(unit_of_work: UnitOfWork):
    try:
        yield
    except IntegrityError as e:
        unit_of_work.rollback()
        print(e)
        raise IntegrityErrorExc("Registro duplicado o error de integridad") from e
    except SQLAlchemyError as e:
        unit_of_work.rollback()
        print(e)
        raise DatabaseOperationError("Error general de base de datos") from e
    except Exception as e:
        print(e)
        unit_of_work.rollback()
        raise
