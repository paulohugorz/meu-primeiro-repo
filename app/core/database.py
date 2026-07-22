from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/database/fashion_os.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def resolve_database_url() -> str:
    """Usa DATABASE_URL em produção e preserva SQLite como fallback local."""
    configured_url = os.getenv("DATABASE_URL", "").strip()
    if not configured_url:
        return f"sqlite:///{DB_PATH}"
    if configured_url.startswith("postgres://"):
        return configured_url.replace("postgres://", "postgresql://", 1)
    return configured_url


def connect_args_for(database_url: str) -> dict:
    return {"check_same_thread": False} if database_url.startswith("sqlite:") else {}


DATABASE_URL = resolve_database_url()
engine = create_engine(DATABASE_URL, connect_args=connect_args_for(DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _migrate(conn):
    """Adiciona colunas novas sem Alembic. SQLite não suporta DROP/RENAME via ALTER."""

    def cols(table):
        return {r[1] for r in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}

    def add_if_missing(table, col, typedef):
        if _table_exists(conn, table) and col not in cols(table):
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}"))

    # pecas — colunas DPP (UNIQUE não pode ir no ALTER; index criado separado)
    add_if_missing("pecas", "gtin",       "VARCHAR")
    add_if_missing("pecas", "dpp_uuid",   "VARCHAR")
    add_if_missing("pecas", "dpp_status", "VARCHAR DEFAULT 'rascunho'")
    add_if_missing("pecas", "area_peca_m2", "FLOAT")
    add_if_missing("pecas", "perda_corte_pct", "FLOAT")
    add_if_missing("pecas", "lote_quantidade", "INTEGER")
    add_if_missing("pecas", "pais_fabricacao", "VARCHAR")
    add_if_missing("pecas", "dpp_version", "VARCHAR DEFAULT '1.0'")
    add_if_missing("pecas", "data_publicacao", "DATETIME")
    add_if_missing("pecas", "data_atualizacao", "DATETIME")

    if _table_exists(conn, "pecas"):
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_pecas_gtin     ON pecas(gtin)"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_pecas_dpp_uuid ON pecas(dpp_uuid)"))

    # fichas_tecnicas — colunas DPP adicionadas depois da criação inicial
    add_if_missing("fichas_tecnicas", "composicao_fibras",          "TEXT")
    add_if_missing("fichas_tecnicas", "instrucoes_reparo",          "TEXT")
    add_if_missing("fichas_tecnicas", "instrucoes_fim_de_vida",     "TEXT")
    add_if_missing("fichas_tecnicas", "certificacoes",              "TEXT")
    add_if_missing("fichas_tecnicas", "conteudo_reciclado_pct",     "FLOAT")
    add_if_missing("fichas_tecnicas", "pegada_carbono_kgco2e",      "FLOAT")
    add_if_missing("fichas_tecnicas", "gramatura_g_m2",             "FLOAT")
    add_if_missing("fichas_tecnicas", "agua_litros_kg",             "FLOAT")
    add_if_missing("fichas_tecnicas", "energia_kwh_kg",             "FLOAT")
    add_if_missing("fichas_tecnicas", "carbono_kgco2e_kg",          "FLOAT")
    add_if_missing("fichas_tecnicas", "fonte_agua_litros_kg",       "TEXT")
    add_if_missing("fichas_tecnicas", "fonte_energia_kwh_kg",       "TEXT")
    add_if_missing("fichas_tecnicas", "fonte_carbono_kgco2e_kg",    "TEXT")
    add_if_missing("fichas_tecnicas", "metodologia_fatores_impacto","TEXT")
    add_if_missing("fichas_tecnicas", "area_total_requerida_m2",    "FLOAT")
    add_if_missing("fichas_tecnicas", "area_perdida_m2",            "FLOAT")
    add_if_missing("fichas_tecnicas", "peso_peca_kg",               "FLOAT")
    add_if_missing("fichas_tecnicas", "agua_peca_litros",           "FLOAT")
    add_if_missing("fichas_tecnicas", "energia_peca_kwh",           "FLOAT")
    add_if_missing("fichas_tecnicas", "evidencia_statuses",         "TEXT")
    add_if_missing("fichas_tecnicas", "durabilidade_ciclos_lavagem","INTEGER")
    # unidade original da fonte — obrigatoria para publicacao (B0 gate)
    add_if_missing("fichas_tecnicas", "agua_unit_source",           "VARCHAR")
    add_if_missing("fichas_tecnicas", "energia_unit_source",        "VARCHAR")
    # faixas de incerteza — opcionais, ativadas em B3
    add_if_missing("fichas_tecnicas", "agua_peca_incerteza_min",    "FLOAT")
    add_if_missing("fichas_tecnicas", "agua_peca_incerteza_max",    "FLOAT")
    add_if_missing("fichas_tecnicas", "carbono_peca_incerteza_min", "FLOAT")
    add_if_missing("fichas_tecnicas", "carbono_peca_incerteza_max", "FLOAT")

    # etapas_producao — coluna GLN adicionada depois
    add_if_missing("etapas_producao", "instalacao_gln", "VARCHAR")

    # peca_materiais — criada inteiramente via create_all (tabela nova)

    # fornecedores — colunas adicionadas após criação inicial
    add_if_missing("fornecedores", "conformidade_social", "VARCHAR DEFAULT 'nao_verificado'")
    add_if_missing("fornecedores", "site",                "VARCHAR")
    add_if_missing("fornecedores", "email_contato",       "VARCHAR")
    add_if_missing("fornecedores", "telefone",            "VARCHAR")
    add_if_missing("fornecedores", "observacoes",         "TEXT")

    # produtos_fornecedor — colunas extras e ISCM
    add_if_missing("produtos_fornecedor", "consumo_agua_litros_kg", "FLOAT")
    add_if_missing("produtos_fornecedor", "risco",                  "TEXT")
    add_if_missing("produtos_fornecedor", "uso_recomendado",        "TEXT")
    add_if_missing("produtos_fornecedor", "disponivel",             "VARCHAR DEFAULT 'a_validar'")
    add_if_missing("produtos_fornecedor", "fonte",                  "VARCHAR DEFAULT 'manual'")
    add_if_missing("produtos_fornecedor", "observacoes",            "TEXT")

    # peca_materiais — quantidade e peso para ponderação mássica no ISCM
    add_if_missing("peca_materiais", "quantidade_m", "FLOAT")
    add_if_missing("peca_materiais", "peso_kg",      "FLOAT")

    # impact_evidences — colunas adicionadas no Sprint 2
    add_if_missing("impact_evidences", "fingerprint",       "VARCHAR")
    add_if_missing("impact_evidences", "nota_curadoria",    "TEXT")
    add_if_missing("impact_evidences", "energia_mj_por_kg", "FLOAT")

    # usage_events v3 — contexto analítico pseudonimizado e versionado
    add_if_missing("usage_events", "event_version", "INTEGER DEFAULT 1")
    add_if_missing("usage_events", "anonymous_id", "VARCHAR")
    add_if_missing("usage_events", "user_id_hash", "VARCHAR")
    add_if_missing("usage_events", "workspace_id_hash", "VARCHAR")
    add_if_missing("usage_events", "source", "VARCHAR")
    add_if_missing("usage_events", "environment", "VARCHAR")
    add_if_missing("usage_events", "application_version", "VARCHAR")
    add_if_missing("usage_events", "request_id", "VARCHAR")


def _table_exists(conn, name: str) -> bool:
    row = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:n"),
        {"n": name},
    ).first()
    return row is not None


def run_migrations():
    with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            _migrate(conn)
            return

        # Migração aditiva segura para o PostgreSQL já criado no Render.
        if inspect(conn).has_table("usage_events"):
            existing = {column["name"] for column in inspect(conn).get_columns("usage_events")}
            columns = {
                "event_version": "INTEGER DEFAULT 1",
                "anonymous_id": "VARCHAR",
                "user_id_hash": "VARCHAR",
                "workspace_id_hash": "VARCHAR",
                "source": "VARCHAR",
                "environment": "VARCHAR",
                "application_version": "VARCHAR",
                "request_id": "VARCHAR",
            }
            for name, typedef in columns.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE usage_events ADD COLUMN {name} {typedef}"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
