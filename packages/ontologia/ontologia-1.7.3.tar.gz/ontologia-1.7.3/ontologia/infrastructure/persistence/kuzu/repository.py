import os
import threading
from typing import TYPE_CHECKING, Any, Optional, cast

from ontologia.config import use_unified_graph_enabled

try:
    import kuzu  # type: ignore[assignment]

    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False
    kuzu: Any = None

if TYPE_CHECKING:
    pass


class KuzuDBRepository:
    _instance: Optional["KuzuDBRepository"] = None
    _lock = threading.Lock()

    db: Any | None = None
    conn: Any | None = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "instance_graph.kuzu"):
        if hasattr(self, "conn"):
            return

        if not KUZU_AVAILABLE:
            print("WARNING: KuzuDB não está instalado. Funcionalidades de grafo desabilitadas.")
            print("         Install com: pip install kuzu")
            self.db = None
            self.conn = None
            return

        assert kuzu is not None  # noqa: S101 - Development assertion

        kuzu_db_path = os.getenv("KUZU_DB_PATH", db_path)
        print(f"INFO: Conectando ao banco de dados de grafo: {kuzu_db_path}")

        database = cast(Any, kuzu.Database(database_path=kuzu_db_path))
        connection = cast(Any, kuzu.Connection(database))
        self.db = database
        self.conn = connection
        use_unified = use_unified_graph_enabled()
        if use_unified:
            print(
                "INFO: Unified graph mode enabled; skipping KuzuDBRepository auto schema initialization."
            )
        else:
            self._initialize_schema()

    def _initialize_schema(self):
        if not self.conn:
            return

        print("INFO: Inicializando/verificando schema do KuzuDB...")

        self.conn.execute(
            """
            CREATE NODE TABLE IF NOT EXISTS Object (
                rid STRING,
                object_type_rid STRING,
                primary_key_value STRING,
                properties STRING,
                PRIMARY KEY (rid)
            )
        """
        )

        self.conn.execute(
            """
            CREATE REL TABLE IF NOT EXISTS LinkedObject (
                FROM Object TO Object,
                rid STRING,
                link_type_rid STRING,
                properties STRING
            )
        """
        )

        print("INFO: Schema do KuzuDB pronto.")

    def is_available(self) -> bool:
        return self.conn is not None

    def execute(self, query: str):
        if not self.is_available():
            raise RuntimeError("KuzuDB não está disponível")
        return self.conn.execute(query)

    def close(self):
        if self.conn:
            self.conn.close()
            print("INFO: Conexão KuzuDB fechada.")


def get_kuzu_repo() -> KuzuDBRepository:
    return KuzuDBRepository()
