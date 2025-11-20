# from sqlalchemy.ext.compiler import compiles
# from sqlalchemy.sql import ClauseElement
# from sqlalchemy.sql.base import Executable
#
#
# class LockTable(Executable, ClauseElement):
#    def __init__(
#        self,
#        element: object = None,
#        exclusive: bool = True,
#        unlock: bool = False,
#        nowait: bool = False,
#    ):
#        """
#        @param element: Table to lock on
#        @param exclusive: True to acquire exclusive lock
#        @param unlock: True to unlock
#        @param nowait: True to fail immediately if the lock is not acquired right away
#        """
#        self.table = element
#        self._option_exclusive = exclusive
#        self._option_unlock = unlock
#        self._option_nowait = nowait
#
#
# @compiles(LockTable)
# def _visit_lock(element, compiler, **kw):
#    raise NotImplementedError()
#
#
# @compiles(LockTable, "postgresql")
# def _visit_lock(element, compiler, **kw):
#    if not element._option_unlock:
#        mode = " ".join(
#            filter(
#                lambda x: x is not None,
#                [
#                    "ACCESS EXCLUSIVE" if element._option_exclusive else None,
#                ],
#            )
#        )
#        tables = ", ".join(
#            [compiler.process(t.__table__, asfrom=True, **kw) for t in element.table]
#        )
#        wait = "NOWAIT" if element._option_nowait else ""
#        return "LOCK TABLE %s IN %s MODE %s" % (tables, mode, wait)
#    elif element._option_unlock:
#        # Table lock released at transaction end: https://www.postgresql.org/docs/current/sql-lock.html
#        return "SELECT TRUE"
