import json
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import listar_publicacoes_dpp, publicar_dpp
from app.core.database import Base
from app.models.models import DppPublicationRecord, EtapaProducao, FichaTecnica, Peca


class DppRouteTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_publicar_dpp_is_idempotent_for_same_piece(self):
        peca = Peca(
            codigo="DPP-IDEMP",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-idempotente",
            pais_fabricacao="BR",
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        self.db.add(peca)
        self.db.flush()
        self.db.add(FichaTecnica(
            peca_id=peca.id,
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            fonte_agua_litros_kg="Fator interno agua",
            fonte_energia_kwh_kg="Fator interno energia",
            fonte_carbono_kgco2e_kg="Fator interno carbono",
            agua_unit_source="L/kg",
            energia_unit_source="kWh/kg",
        ))
        self.db.add(EtapaProducao(
            peca_id=peca.id,
            etapa="costura",
            pais="BR",
            instalacao_nome="Atelie Piloto",
        ))
        self.db.commit()

        first = publicar_dpp("DPP-IDEMP", db=self.db)
        first_publication_date = first.data_publicacao
        first_update_date = first.data_atualizacao

        second = publicar_dpp("DPP-IDEMP", db=self.db)

        self.assertEqual(self.db.query(Peca).filter(Peca.codigo == "DPP-IDEMP").count(), 1)
        self.assertEqual(second.dpp_status, "publicado")
        self.assertEqual(second.dpp_uuid, "uuid-idempotente")
        self.assertEqual(second.data_publicacao, first_publication_date)
        self.assertGreaterEqual(second.data_atualizacao, first_update_date)
        records = self.db.query(DppPublicationRecord).all()
        self.assertEqual(len(records), 2)
        self.assertTrue(all(record.resultado == "aprovado" for record in records))
        self.assertTrue(all(len(record.snapshot_sha256) == 64 for record in records))

    def test_publicar_dpp_accepts_tier1_with_uuid_without_gtin(self):
        peca = Peca(
            codigo="DPP-TIER1",
            nome="Camiseta Tier 1",
            gtin=None,
            dpp_uuid="uuid-tier1",
            pais_fabricacao="BR",
        )
        self.db.add(peca)
        self.db.flush()
        self.db.add(FichaTecnica(
            peca_id=peca.id,
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            instrucoes_reparo="Lavar com agua fria e secar a sombra",
            instrucoes_fim_de_vida="Doar, reparar ou encaminhar para reciclagem textil",
        ))
        self.db.add(EtapaProducao(
            peca_id=peca.id,
            etapa="costura",
            pais="BR",
            instalacao_nome="Atelie Piloto",
        ))
        self.db.commit()

        result = publicar_dpp("DPP-TIER1", db=self.db)

        self.assertEqual(result.dpp_status, "publicado")
        self.assertEqual(result.gtin, None)
        self.assertEqual(result.dpp_uuid, "uuid-tier1")
        self.assertEqual(result.ficha_tecnica.agua_peca_litros, None)

        history = listar_publicacoes_dpp("DPP-TIER1", db=self.db)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["resultado"], "aprovado")
        self.assertEqual(history[0]["snapshot"]["dpp_uuid"], "uuid-tier1")
        self.assertEqual(history[0]["snapshot"]["evidence_statuses"]["composicao_fibras"], "declarado")

    def test_publicar_dpp_records_blocked_gate_without_generating_uuid(self):
        peca = Peca(codigo="DPP-BLOCK", nome="Peça incompleta")
        self.db.add(peca)
        self.db.flush()
        self.db.add(FichaTecnica(peca_id=peca.id))
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            publicar_dpp("DPP-BLOCK", db=self.db)
        self.assertEqual(context.exception.status_code, 422)

        self.db.refresh(peca)
        record = self.db.query(DppPublicationRecord).one()
        self.assertEqual(record.resultado, "bloqueado")
        self.assertIsNone(record.snapshot_json)
        self.assertIsNone(record.snapshot_sha256)
        self.assertIsNone(peca.dpp_uuid)
        self.assertTrue(json.loads(record.errors))


if __name__ == "__main__":
    unittest.main()
