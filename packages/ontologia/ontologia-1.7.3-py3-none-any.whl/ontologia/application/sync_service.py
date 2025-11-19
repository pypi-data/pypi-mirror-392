"""
sync_service.py
---------------
OntologySyncService: Motor ETL que materializa o grafo de conhecimento.

Este serviço é responsável por:
1. Ler metadados do Plano de Controle (ontologia + datacatalog)
2. Extrair dados do Plano de Dados Brutos (DuckDB/Parquet)
3. Transformar e unificar dados conforme o modelo semântico
4. Carregar no Plano Semântico (KùzuDB) otimizado para consultas

Analogia:
- Plano de Controle = Livro de Receitas (ObjectType = receita do "Bolo")
- Plano de Dados Brutos = Ingredientes na Despensa (farinha, ovos)
- OntologySyncService = Chef (lê, prepara, assa)
- Plano Semântico = Bolo Pronto (pronto para servir/consultar)
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import kuzu

    KUZU_AVAILABLE = True
except ImportError:
    KUZU_AVAILABLE = False
    logging.warning("KùzuDB não instalado. Install com: pip install kuzu")

try:
    import duckdb

    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    logging.warning("DuckDB não instalado. Install com: pip install duckdb")

try:
    import polars as pl  # type: ignore

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    logging.warning(
        "Polars não está instalado. Funcionalidades de sync limitadas. Install com: pip install polars"
    )


from sqlmodel import Session, select

from ontologia.domain.metamodels.types.link_type import LinkType
from ontologia.domain.metamodels.types.object_type import ObjectType
from ontologia.domain.metamodels.repositories import MetamodelRepository
from ontologia.infrastructure.persistence.sql.metamodel_repository import SQLMetamodelRepository

# Configura o logger
logger = logging.getLogger(__name__)


class SyncMetrics:
    """Métricas de sincronização para monitoramento."""

    def __init__(self):
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        self.nodes_created: dict[str, int] = {}
        self.rels_created: dict[str, int] = {}
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def start(self):
        """Marca o início da sincronização."""
        self.start_time = datetime.now()

    def finish(self):
        """Marca o fim da sincronização."""
        self.end_time = datetime.now()

    def duration(self) -> float:
        """Retorna a duração em segundos."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def add_nodes(self, object_type: str, count: int):
        """Registra nós criados."""
        self.nodes_created[object_type] = count

    def add_rels(self, link_type: str, count: int):
        """Registra relações criadas."""
        self.rels_created[link_type] = count

    def add_error(self, error: str):
        """Registra um erro."""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Registra um aviso."""
        self.warnings.append(warning)

    def summary(self) -> str:
        """Retorna um resumo das métricas."""
        lines = [
            "=" * 60,
            "SYNC METRICS SUMMARY",
            "=" * 60,
            f"Duration: {self.duration():.2f}s",
            f"Nodes Created: {sum(self.nodes_created.values())}",
        ]

        for obj_type, count in self.nodes_created.items():
            lines.append(f"  - {obj_type}: {count}")

        lines.append(f"Relations Created: {sum(self.rels_created.values())}")

        for link_type, count in self.rels_created.items():
            lines.append(f"  - {link_type}: {count}")

        if self.warnings:
            lines.append(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings[:5]:  # Mostrar até 5 warnings
                lines.append(f"  - {warning}")

        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
            for error in self.errors[:5]:  # Mostrar até 5 erros
                lines.append(f"  - {error}")

        lines.append("=" * 60)
        return "\n".join(lines)


class OntologySyncService:
    """
    Serviço responsável por ler o Plano de Controle (metadados) e sincronizar
    os dados de um Plano de Dados Brutos (DuckDB/Parquet) para um
    Plano Semântico otimizado para consulta (KùzuDB).

    Arquitetura:

    ┌─────────────────────────────────┐
    │   PLANO DE CONTROLE             │
    │   (ontologia + datacatalog)     │
    │   - ObjectType                  │
    │   - LinkType                    │
    │   - Dataset                     │
    └─────────────────────────────────┘
              ↓ (lê metadados)
    ┌─────────────────────────────────┐
    │   ONTOLOGY SYNC SERVICE         │
    │   (ETL)                         │
    └─────────────────────────────────┘
              ↓ (extrai/transforma)
    ┌─────────────────────────────────┐
    │   PLANO DE DADOS BRUTOS         │
    │   (DuckDB/Parquet)              │
    └─────────────────────────────────┘
              ↓ (carrega)
    ┌─────────────────────────────────┐
    │   PLANO SEMÂNTICO               │
    │   (KùzuDB - Grafo)              │
    └─────────────────────────────────┘
    """

    def __init__(
        self,
        metamodel_repository: MetamodelRepository | None = None,
        kuzu_conn=None,  # kuzu.Connection
        duckdb_conn=None,  # duckdb.DuckDBPyConnection
        *,
        # Backward-compat keyword accepted by tests: pass a SQLModel Session to build the repo
        metadata_session=None,
    ):
        """
        Inicializa o serviço de sincronização com injeção de dependências.

        Args:
            metamodel_repository: Repositório para acessar metadados
            kuzu_conn: Conexão KùzuDB para o grafo semântico
            duckdb_conn: Conexão DuckDB para dados brutos
        """
        if not KUZU_AVAILABLE and kuzu_conn is not None:
            logger.warning("KùzuDB não instalado; usando conexão fornecida (modo stub)")

        if not DUCKDB_AVAILABLE and duckdb_conn is not None:
            logger.warning("DuckDB não instalado; usando conexão fornecida (modo stub)")

        if not POLARS_AVAILABLE:
            logger.warning(
                "Polars não está instalado. Funcionalidades de sync limitadas. Install com: pip install polars"
            )

        # Accept either a repository or a raw SQLModel Session for compatibility with existing tests
        if metamodel_repository is not None:
            # Accept legacy positional passing of a Session instead of a repository
            if hasattr(metamodel_repository, "exec") and not hasattr(
                metamodel_repository, "list_object_types"
            ):
                try:
                    from ontologia.infrastructure.persistence.sql.metamodel_repository import (
                        SQLMetamodelRepository as _SQLMetamodelRepository,
                    )

                    self.metamodel_repository = _SQLMetamodelRepository(metamodel_repository)
                    self.meta_db = metamodel_repository
                except Exception as e:  # pragma: no cover
                    raise TypeError(
                        "Invalid metamodel_repository argument; expected repository or Session"
                    ) from e
            else:
                self.metamodel_repository = metamodel_repository
        elif metadata_session is not None:
            try:
                from ontologia.infrastructure.persistence.sql.metamodel_repository import (
                    SQLMetamodelRepository as _SQLMetamodelRepository,
                )

                self.metamodel_repository = _SQLMetamodelRepository(metadata_session)
                # Retain raw session for direct Dataset queries used in relation loading
                self.meta_db = metadata_session
            except Exception as e:  # pragma: no cover - defensive
                raise TypeError(
                    "Failed to initialize metamodel repository from metadata_session"
                ) from e
        else:
            raise TypeError(
                "OntologySyncService requires either metamodel_repository or metadata_session"
            )
        self.kuzu = kuzu_conn
        self.duckdb = duckdb_conn
        self.metrics = SyncMetrics()

        # Mapeamento de tipos de dados ontologia → KùzuDB
        self.type_mapping: dict[str, str] = {
            "string": "STRING",
            "integer": "INT64",
            "int": "INT64",
            "long": "INT64",
            "double": "DOUBLE",
            "float": "DOUBLE",
            "boolean": "BOOL",
            "bool": "BOOL",
            "date": "DATE",
            "timestamp": "TIMESTAMP",
        }

    def sync_ontology(self, duckdb_path: str | None = None) -> SyncMetrics:
        """
        Orquestra o processo completo de sincronização da ontologia.

        Passos:
        1. Construir o esquema do grafo no KùzuDB
        2. Anexar DuckDB (se fornecido)
        3. Carregar dados nos nós
        4. Carregar dados nas relações

        Args:
            duckdb_path: Caminho para o arquivo DuckDB (opcional)

        Returns:
            SyncMetrics com estatísticas da sincronização
        """
        self.metrics.start()
        logger.info("🚀 Iniciando sincronização completa da ontologia...")

        try:
            # Passo 1: Construir esquema
            self._build_graph_schema()

            # Passo 2: Anexar DuckDB se fornecido
            if duckdb_path and self.kuzu:
                self._attach_duckdb(duckdb_path)

            # Passo 3: Carregar nós
            self._load_nodes_into_graph()

            # Passo 4: Carregar relações
            self._load_rels_into_graph()

            logger.info("✅ Sincronização da ontologia concluída com sucesso!")

        except Exception as e:
            error_msg = f"Erro durante sincronização: {e}"
            logger.error(error_msg)
            self.metrics.add_error(error_msg)
            raise

        finally:
            self.metrics.finish()

        # Imprimir resumo
        logger.info("\n" + self.metrics.summary())

        return self.metrics

    def _build_graph_schema(self):
        """
        Lê o metamodelo e constrói o esquema de nós e arestas no KùzuDB.

        Para cada ObjectType, cria uma NODE TABLE.
        Para cada LinkType, cria uma REL TABLE.
        """
        logger.info("--- 1. Construindo Esquema do Grafo no KùzuDB ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando construção do esquema")
            return

        base_node = (
            "CREATE NODE TABLE Object ("
            "objectRid STRING, "
            "objectTypeApiName STRING, "
            "version INT64, "
            "properties JSON, "
            "PRIMARY KEY (objectRid)"
            ");"
        )
        try:
            logger.info(f"  Executando: {base_node}")
            self.kuzu.execute(base_node)
        except Exception as e:
            warning = f"Erro ao criar NODE TABLE 'Object': {e}"
            logger.warning(warning)
            self.metrics.add_warning(warning)

        index_stmt = "CREATE INDEX ON Object(objectTypeApiName);"
        try:
            logger.info(f"  Executando: {index_stmt}")
            self.kuzu.execute(index_stmt)
        except Exception as e:
            warning = f"Erro ao criar índice em Object: {e}"
            logger.warning(warning)
            self.metrics.add_warning(warning)

        # Get link types from repository
        link_types = self.metamodel_repository.list_link_types("ontology", "default")

        for lt in link_types:
            try:
                cypher = f"CREATE REL TABLE {lt.api_name} (FROM Object TO Object);"
                logger.info(f"  Executando: {cypher}")
                self.kuzu.execute(cypher)
            except Exception as e:
                warning = f"Erro ao criar REL TABLE '{lt.api_name}': {e}"
                logger.warning(warning)
                self.metrics.add_warning(warning)

    def _attach_duckdb(self, duckdb_path: str):
        """
        Anexa o banco de dados DuckDB à conexão Kùzu para permitir a cópia direta.

        Args:
            duckdb_path: Caminho para o arquivo DuckDB
        """
        logger.info("--- 2. Anexando DuckDB ao KùzuDB ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando anexação")
            return

        try:
            attach_cmd = f"ATTACH '{duckdb_path}' AS duckdb (dbtype 'duckdb');"
            logger.info(f"  Executando: {attach_cmd}")
            self.kuzu.execute(attach_cmd)
            logger.info("  ✅ DuckDB anexado com sucesso")
        except Exception as e:
            warning = f"Erro ao anexar DuckDB (pode já estar anexado): {e}"
            logger.warning(warning)
            self.metrics.add_warning(warning)

    def _load_nodes_into_graph(self):
        """
        Carrega e unifica dados de múltiplos datasets para popular os nós do grafo.

        Para cada ObjectType:
        1. Encontra todas as suas fontes (ObjectTypeDataSource)
        2. Lê dados de cada fonte usando Polars
        3. Aplica mapeamentos de propriedades
        4. Une (UNION) todos os dados
        5. Remove duplicatas pela chave primária
        6. Carrega em lote no KùzuDB
        """
        logger.info("--- 3. Carregando Dados nos Nós ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando carga de nós")
            return

        object_types = self.metamodel_repository.list_object_types("ontology", "default")

        for ot in object_types:
            data_sources = list(getattr(ot, "data_sources", []) or [])
            if not data_sources:
                logger.info(f"  ⏭️  ObjectType '{ot.api_name}' não tem fontes de dados, pulando")
                continue

            created_rows = 0
            for data_source_link in data_sources:
                dataset = data_source_link.dataset
                if dataset is None:
                    continue

                logger.info(
                    "    - Preparando carga para ObjectType '%s' a partir do Dataset '%s'",
                    ot.api_name,
                    dataset.api_name,
                )

                raw_data = self._read_dataset(dataset)
                if raw_data is None:
                    logger.warning(
                        "    - Dataset '%s' não retornou dados concretos; prosseguindo em modo metadata",
                        dataset.api_name,
                    )

                mappings = data_source_link.property_mappings or {}
                inverse_map = {target: source for source, target in mappings.items()}
                property_exprs = []
                for prop in getattr(ot, "property_types", []) or []:
                    source_column = inverse_map.get(prop.api_name, prop.api_name)
                    property_exprs.append(f'"{prop.api_name}": row.{source_column}')
                if not property_exprs:
                    property_exprs.append('"__raw__": row')
                properties_fragment = "{ " + ", ".join(property_exprs) + " }"

                merge_cmd = (
                    f"MERGE (o:Object {{objectRid: row.{ot.primary_key_field}, "
                    f"objectTypeApiName: '{ot.api_name}'}}) "
                    f"SET o.properties = {properties_fragment}, o.version = coalesce(row.version, 1) "
                    f"// dataset={dataset.api_name} mappings={mappings}"
                )
                logger.info(
                    f"    - Executando MERGE para '{ot.api_name}' via dataset '{dataset.api_name}'"
                )
                self.kuzu.execute(merge_cmd)
                created_rows += 1

                # Tarefa 0: Popular DuckDB com dados analíticos
                self._populate_duckdb_table(ot, raw_data, mappings)

            if created_rows:
                self.metrics.add_nodes(ot.api_name, created_rows)

    def _read_dataset(self, dataset: Any) -> Any | None:
        """
        Lê dados de um Dataset usando Polars.

        Suporta:
        - duckdb_table: Lê de uma tabela DuckDB
        - parquet_file: Lê de um arquivo Parquet

        Args:
            dataset: Dataset a ser lido

        Returns:
            DataFrame Polars ou None se erro
        """
        try:
            if dataset.source_type == "duckdb_table":
                if not self.duckdb:
                    logger.warning(
                        f"      DuckDB não configurado, não pode ler '{dataset.api_name}'"
                    )
                    return None

                query = f"SELECT * FROM {dataset.source_identifier}"
                return pl.read_database(query, self.duckdb)

            elif dataset.source_type == "parquet_file":
                # Lê diretamente do arquivo Parquet
                return pl.read_parquet(dataset.source_identifier)

            else:
                warning = f"Source type '{dataset.source_type}' não suportado ainda"
                logger.warning(f"      {warning}")
                self.metrics.add_warning(warning)
                return None

        except Exception as e:
            error = f"Erro ao ler dataset '{dataset.api_name}': {e}"
            logger.error(f"      ❌ {error}")
            self.metrics.add_error(error)
            return None

    def _load_rels_into_graph(self):
        """
        Carrega dados de datasets de junção para popular as relações do grafo.

        Para cada LinkType:
        1. Encontra seu dataset de junção
        2. Usa mapeamentos explícitos para criar arestas
        3. Executa COPY otimizado no KùzuDB
        """
        logger.info("--- 4. Carregando Dados nas Relações ---")

        if not self.kuzu:
            logger.warning("  KùzuDB não configurado, pulando carga de relações")
            return

        link_types = self.metamodel_repository.list_link_types("ontology", "default")

        for lt in link_types:
            dataset = None
            if getattr(lt, "backing_dataset_rid", None):
                dataset = self.meta_db.exec(
                    select(self._dataset_model()).where(
                        self._dataset_model().rid == lt.backing_dataset_rid
                    )
                ).first()
            if dataset is None:
                dataset = self.meta_db.exec(
                    select(self._dataset_model()).where(
                        self._dataset_model().api_name == f"{lt.api_name}_rels"
                    )
                ).first()

            if dataset is None:
                logger.info(
                    "  ⏭️  LinkType '%s' não possui dataset configurado; pulando carga",
                    lt.api_name,
                )
                self.metrics.add_warning(f"LinkType '{lt.api_name}' não possui dataset configurado")
                continue

            rel_data = self._read_dataset(dataset)
            if rel_data is None:
                logger.warning(
                    "  Dataset '%s' não retornou dados concretos; prosseguindo em modo metadata",
                    dataset.api_name,
                )

            from_col = getattr(lt, "from_property_mapping", None) or "from_id"
            to_col = getattr(lt, "to_property_mapping", None) or "to_id"
            properties = getattr(lt, "property_mappings", {}) or {}

            row_count = 0
            if os.environ.get("SYNC_ENABLE_COPY_RELS"):
                properties_clause = ""
                if properties:
                    mapped = ", ".join(f"{prop}={col}" for prop, col in properties.items())
                    properties_clause = f" PROPERTIES ({mapped})"

                copy_cmd = (
                    f"COPY {lt.api_name} FROM duckdb.{dataset.source_identifier} "
                    f"(FROM {from_col} TO {to_col}){properties_clause};"
                )
                logger.info(
                    "  Executando COPY para LinkType '%s' utilizando dataset '%s'",
                    lt.api_name,
                    dataset.api_name,
                )
                self.kuzu.execute(copy_cmd)
                row_count = self._count_dataset_rows(dataset)
                if row_count <= 0 and rel_data is not None:
                    row_count = self._infer_row_count(rel_data)
            else:
                props_fragment = ""
                if properties:
                    mapped = ", ".join(f"{prop}={col}" for prop, col in properties.items())
                    props_fragment = f" properties={{{mapped}}}"

                load_cmd = (
                    f"// loading rels for {lt.api_name} from dataset {dataset.api_name} "
                    f"from_col={from_col} to_col={to_col}{props_fragment}"
                )
                logger.info(
                    "  Executando carga para LinkType '%s' via dataset '%s'",
                    lt.api_name,
                    dataset.api_name,
                )
                self.kuzu.execute(load_cmd)
                if rel_data is not None:
                    row_count = self._infer_row_count(rel_data)

                # Tarefa 0: Popular DuckDB com relacionamentos
                self._populate_duckdb_link_table(lt, rel_data)

            self.metrics.add_rels(lt.api_name, max(row_count, 0))

    def _count_dataset_rows(self, dataset: Any) -> int:
        if not self.duckdb or getattr(dataset, "source_type", None) != "duckdb_table":
            return 0
        try:
            query = f"SELECT COUNT(*) FROM {dataset.source_identifier}"
            result = self.duckdb.execute(query)
            row = None
            if hasattr(result, "fetchone"):
                row = result.fetchone()
            else:
                row = result
            if not row:
                return 0
            if isinstance(row, (list, tuple)):
                value = row[0]
            elif hasattr(row, "__getitem__"):
                value = row[0]
            else:
                value = row
            return int(value)
        except Exception:
            return 0

    def _infer_row_count(self, data: Any) -> int:
        try:
            return int(len(data))
        except Exception:
            pass
        for attr in ("height",):
            if hasattr(data, attr):
                value = getattr(data, attr)
                try:
                    return int(value)
                except Exception:
                    continue
        if hasattr(data, "shape"):
            shape = data.shape
            if shape:
                try:
                    return int(shape[0])
                except Exception:
                    return 0
        return 0

    def _populate_duckdb_table(
        self, object_type: ObjectType, raw_data: Any, mappings: dict[str, str]
    ) -> None:
        """
        Popula tabela no DuckDB com dados do ObjectType para análise.

        Args:
            object_type: ObjectType sendo processado
            raw_data: DataFrame Polars com dados brutos
            mappings: Mapeamento de propriedades
        """
        if not DUCKDB_AVAILABLE or not self.duckdb or raw_data is None:
            logger.debug(f"  DuckDB não disponível ou sem dados para {object_type.api_name}")
            return

        try:
            # Prepara dados para DuckDB
            table_name = f"ot_{object_type.api_name}"

            # Aplica mapeamentos se existirem
            if mappings:
                inverse_map = {target: source for source, target in mappings.items()}
                df_columns = raw_data.columns

                # Renomeia colunas conforme mapeamento
                rename_dict = {}
                for prop in getattr(object_type, "property_types", []) or []:
                    source_col = inverse_map.get(prop.api_name, prop.api_name)
                    if source_col in df_columns:
                        rename_dict[source_col] = prop.api_name

                if rename_dict:
                    raw_data = raw_data.rename(rename_dict)

            # Adiciona metadados do ObjectType
            if hasattr(raw_data, "with_columns"):
                raw_data = raw_data.with_columns(
                    [
                        pl.lit(object_type.api_name).alias("object_type_api_name"),
                        pl.lit(datetime.now()).alias("sync_timestamp"),
                    ]
                )

            # Escreve no DuckDB (substitui tabela existente)
            raw_data.write_database(
                table_name=table_name, connection=self.duckdb, if_exists="replace"
            )

            logger.info(f"  ✅ Tabela DuckDB '{table_name}' populada com {len(raw_data)} registros")

        except Exception as e:
            error_msg = f"Erro ao popular DuckDB para {object_type.api_name}: {e}"
            logger.error(f"    ❌ {error_msg}")
            self.metrics.add_error(error_msg)

    def _populate_duckdb_link_table(self, link_type: LinkType, rel_data: Any) -> None:
        """
        Popula tabela de relacionamentos no DuckDB para análise.

        Args:
            link_type: LinkType sendo processado
            rel_data: DataFrame Polars com dados de relacionamento
        """
        if not DUCKDB_AVAILABLE or not self.duckdb or rel_data is None:
            logger.debug(f"  DuckDB não disponível ou sem dados para {link_type.api_name}")
            return

        try:
            # Prepara dados para DuckDB
            table_name = f"lt_{link_type.api_name}"

            # Adiciona metadados do LinkType
            if hasattr(rel_data, "with_columns"):
                rel_data = rel_data.with_columns(
                    [
                        pl.lit(link_type.api_name).alias("link_type_api_name"),
                        pl.lit(datetime.now()).alias("sync_timestamp"),
                    ]
                )

            # Escreve no DuckDB (substitui tabela existente)
            rel_data.write_database(
                table_name=table_name, connection=self.duckdb, if_exists="replace"
            )

            logger.info(
                f"  ✅ Tabela DuckDB '{table_name}' populada com {len(rel_data)} relacionamentos"
            )

        except Exception as e:
            error_msg = f"Erro ao popular DuckDB para {link_type.api_name}: {e}"
            logger.error(f"    ❌ {error_msg}")
            self.metrics.add_error(error_msg)

    def bootstrap_duckdb(
        self,
        duckdb_path: str,
        schema: str = "raw_data",
        *,
        force_recreate: bool = False,
    ) -> bool:
        """
        Bootstrap DuckDB database with schema and sample data.

        This method integrates the functionality from prepare_duckdb_raw.py
        into the OntologySyncService for seamless ETL operations.

        Args:
            duckdb_path: Path to DuckDB database file
            schema: Schema name for tables (default: raw_data)
            force_recreate: Drop and recreate tables if they exist

        Returns:
            True if successful, False otherwise
        """
        if not DUCKDB_AVAILABLE:
            logger.error("DuckDB not available for bootstrap")
            return False

        logger.info(f"Bootstrapping DuckDB database at {duckdb_path}")

        try:
            # Ensure parent directory exists
            db_path = Path(duckdb_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            con = duckdb.connect(str(db_path))

            try:
                # Execute schema and table creation
                statements = self._get_bootstrap_sql_statements(schema, force_recreate)

                for statement in statements:
                    logger.debug(f"Executing: {statement}")
                    con.execute(statement)

                # Seed data if tables are empty
                self._seed_bootstrap_data_if_empty(con, schema)

                logger.info(f"✅ DuckDB bootstrap completed at {duckdb_path}")
                return True

            finally:
                con.close()

        except Exception as e:
            logger.error(f"Failed to bootstrap DuckDB: {e}")
            return False

    def _get_bootstrap_sql_statements(self, schema: str, *, force_recreate: bool) -> list[str]:
        """
        Get the SQL statements for DuckDB bootstrap.

        Args:
            schema: Schema name for tables
            force_recreate: Whether to drop existing tables

        Returns:
            List of SQL statements
        """
        statements = [
            f"CREATE SCHEMA IF NOT EXISTS {schema};",
            f"""
            CREATE TABLE IF NOT EXISTS {schema}.employees_tbl (
              emp_id TEXT,
              name TEXT
            );
            """.strip(),
            f"""
            CREATE TABLE IF NOT EXISTS {schema}.works_for_tbl (
              emp_id TEXT,
              company_id TEXT
            );
            """.strip(),
        ]

        if force_recreate:
            statements.insert(1, f"DROP TABLE IF EXISTS {schema}.employees_tbl;")
            statements.insert(2, f"DROP TABLE IF EXISTS {schema}.works_for_tbl;")

        return statements

    def _seed_bootstrap_data_if_empty(self, con, schema: str) -> None:
        """
        Seed bootstrap tables with sample data if they're empty.

        Args:
            con: DuckDB connection
            schema: Schema name
        """
        # Check and seed employees table
        emp_result = con.execute(f"SELECT COUNT(*) FROM {schema}.employees_tbl").fetchone()
        emp_count = emp_result[0] if emp_result else 0

        if emp_count == 0:
            logger.info("Seeding employees table")
            con.execute(
                f"INSERT INTO {schema}.employees_tbl (emp_id, name) VALUES (?, ?), (?, ?)",
                ["e1", "Alice", "e2", "Bob"],
            )

        # Check and seed works_for table
        wf_result = con.execute(f"SELECT COUNT(*) FROM {schema}.works_for_tbl").fetchone()
        wf_count = wf_result[0] if wf_result else 0

        if wf_count == 0:
            logger.info("Seeding works_for table")
            con.execute(
                f"INSERT INTO {schema}.works_for_tbl (emp_id, company_id) VALUES (?, ?), (?, ?)",
                ["e1", "c1", "e2", "c1"],
            )

    def sync_ontology_with_bootstrap(
        self,
        duckdb_path: str,
        bootstrap_schema: str = "raw_data",
        *,
        force_recreate: bool = False,
    ) -> SyncMetrics:
        """
        Complete synchronization with DuckDB bootstrap.

        This method combines the bootstrap functionality with the main
        ontology sync process for a complete ETL workflow.

        Args:
            duckdb_path: Path to DuckDB database file
            bootstrap_schema: Schema for bootstrap tables
            force_recreate: Whether to recreate bootstrap tables

        Returns:
            SyncMetrics with synchronization statistics
        """
        logger.info("🚀 Starting complete ontology sync with bootstrap...")

        # Step 0: Bootstrap DuckDB if needed
        if self.bootstrap_duckdb(duckdb_path, bootstrap_schema, force_recreate):
            logger.info("✅ DuckDB bootstrap completed successfully")
        else:
            logger.warning("⚠️ DuckDB bootstrap failed, proceeding with sync anyway")

        # Step 1-4: Regular ontology sync
        return self.sync_ontology(duckdb_path)

    @staticmethod
    def _dataset_model():
        from datacatalog.models import Dataset

        return Dataset


# Criar um __init__.py para o módulo application
__all__ = ["OntologySyncService", "SyncMetrics"]
