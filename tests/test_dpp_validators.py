import json
from types import SimpleNamespace
import unittest

from app.validators.dpp_validators import (
    build_evidence_statuses,
    validate_dpp_publication,
    validate_fiber_composition,
)


def make_peca(**overrides):
    data = {
        "codigo": "DPP-TESTE",
        "nome": "Camiseta Teste",
        "gtin": "7891234567890",
        "dpp_uuid": "uuid-teste",
        "pais_fabricacao": "BR",
        "area_peca_m2": 1,
        "perda_corte_pct": 20,
        "lote_quantidade": 100,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def make_ficha(**overrides):
    data = {
        "composicao_fibras": json.dumps([{"fibra": "algodao", "pct": 100}]),
        "instrucoes_reparo": "Lavar com sabao neutro e secar a sombra.",
        "instrucoes_fim_de_vida": "Encaminhar para reuso, reparo ou descarte textil adequado.",
        "certificacoes": None,
        "gramatura_g_m2": 200,
        "agua_litros_kg": 100,
        "energia_kwh_kg": 10,
        "carbono_kgco2e_kg": 2,
        "fonte_agua_litros_kg": "Fator interno agua",
        "fonte_energia_kwh_kg": "Fator interno energia",
        "fonte_carbono_kgco2e_kg": "Fator interno carbono",
        "metodologia_fatores_impacto": "Estimativa calculada; nao substitui ACV oficial",
        "agua_peca_litros": 25,
        "energia_peca_kwh": 2.5,
        "pegada_carbono_kgco2e": 0.5,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


class DppValidatorTests(unittest.TestCase):
    def test_validate_fiber_composition_requires_100_percent_total(self):
        with self.assertRaisesRegex(ValueError, "100%"):
            validate_fiber_composition(json.dumps([
                {"fibra": "algodao", "pct": 80},
                {"fibra": "elastano", "pct": 10},
            ]))

    def test_validate_dpp_publication_rejects_fiber_total_below_100(self):
        peca = SimpleNamespace(
            codigo="CAM-001",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-cam-001",
            tem_pais_fabricacao=True,
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([
                {"fibra": "algodao", "pct": 70},
                {"fibra": "elastano", "pct": 20},
            ]),
            certificacoes=None,
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            fonte_agua_litros_kg="Base setorial documentada Textile Exchange",
            fonte_energia_kwh_kg="Base setorial documentada Higg MSI",
            fonte_carbono_kgco2e_kg="Fator de emissao documentado GHG Protocol",
            metodologia_fatores_impacto="Estimativa calculada; nao substitui ACV oficial",
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
            agua_peca_litros=25,
            energia_peca_kwh=2.5,
            pegada_carbono_kgco2e=0.5,
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertFalse(result.can_publish)
        self.assertIn("composicao_fibras deve somar 100%", result.errors)

    def test_validate_dpp_publication_reports_missing_fields_once(self):
        peca = SimpleNamespace(
            codigo=None,
            nome=None,
            gtin=None,
            dpp_uuid=None,
            tem_pais_fabricacao=False,
            area_peca_m2=None,
            perda_corte_pct=None,
            lote_quantidade=None,
        )
        ficha = SimpleNamespace(
            composicao_fibras=None,
            certificacoes=None,
            instrucoes_reparo=None,
            instrucoes_fim_de_vida=None,
            gramatura_g_m2=None,
            agua_litros_kg=None,
            energia_kwh_kg=None,
            carbono_kgco2e_kg=None,
            agua_peca_litros=None,
            energia_peca_kwh=None,
            pegada_carbono_kgco2e=None,
            fonte_agua_litros_kg=None,
            fonte_energia_kwh_kg=None,
            fonte_carbono_kgco2e_kg=None,
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertFalse(result.can_publish)
        self.assertEqual(
            sum("composicao_fibras" in error for error in result.errors),
            1,
        )
        self.assertEqual(sum("SKU" in error for error in result.errors), 1)
        self.assertEqual(sum("nome da peca" in error for error in result.errors), 1)
        self.assertEqual(sum("pais de fabricacao" in error for error in result.errors), 1)
        self.assertEqual(sum("cuidado/lavagem" in error for error in result.errors), 1)
        self.assertEqual(sum("fim de vida" in error for error in result.errors), 1)
        self.assertFalse(any("area da peca obrigatoria" in error for error in result.errors))
        self.assertFalse(any("fator de agua obrigatorio" in error for error in result.errors))

    def test_validate_dpp_publication_warns_for_expired_cert_without_blocking(self):
        peca = SimpleNamespace(
            codigo="CAM-001",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-cam-001",
            tem_pais_fabricacao=True,
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            certificacoes=json.dumps([{"nome": "OEKO-TEX", "validade": "2000-01-01"}]),
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            agua_peca_litros=25,
            energia_peca_kwh=2.5,
            pegada_carbono_kgco2e=0.5,
            fonte_agua_litros_kg="Fator interno agua",
            fonte_energia_kwh_kg="Fator interno energia",
            fonte_carbono_kgco2e_kg="Fator interno carbono",
            agua_unit_source="L/kg",
            energia_unit_source="kWh/kg",
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertTrue(result.can_publish)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, ["OEKO-TEX: certificado expirado"])

    def test_build_evidence_statuses_handles_missing_ficha(self):
        peca = SimpleNamespace(
            codigo=None,
            nome=None,
            gtin=None,
            dpp_uuid=None,
            tem_pais_fabricacao=False,
            area_peca_m2=None,
            perda_corte_pct=None,
            lote_quantidade=None,
        )

        statuses = build_evidence_statuses(peca, None)

        self.assertTrue(statuses)
        self.assertTrue(all(status == "ausente" for status in statuses.values()))


    def test_validate_dpp_publication_accepts_tier1_without_gtin_or_tier2(self):
        peca = SimpleNamespace(
            codigo="CAM-TIER1",
            nome="Camiseta Tier 1",
            gtin=None,
            dpp_uuid="uuid-tier1",
            tem_pais_fabricacao=True,
            area_peca_m2=None,
            perda_corte_pct=None,
            lote_quantidade=None,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            certificacoes=None,
            instrucoes_reparo="Lavar com agua fria e secar a sombra",
            instrucoes_fim_de_vida="Doar, reparar ou encaminhar para reciclagem textil",
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertTrue(result.can_publish)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.evidence_statuses["identificador_publico"], "declarado")
        self.assertEqual(result.evidence_statuses["composicao_fibras"], "declarado")
        self.assertEqual(result.evidence_statuses["agua_peca_litros"], "ausente")


    def test_validate_dpp_publication_accepts_minimum_evidence_after_calculation(self):
        peca = SimpleNamespace(
            codigo="CAM-001",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-cam-001",
            tem_pais_fabricacao=True,
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            certificacoes=None,
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            agua_peca_litros=25,
            energia_peca_kwh=2.5,
            pegada_carbono_kgco2e=0.5,
            fonte_agua_litros_kg="Fator interno agua",
            fonte_energia_kwh_kg="Fator interno energia",
            fonte_carbono_kgco2e_kg="Fator interno carbono",
            agua_unit_source="L/kg",
            energia_unit_source="kWh/kg",
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertTrue(result.can_publish)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.evidence_statuses["composicao_fibras"], "declarado")
        self.assertEqual(result.evidence_statuses["carbono_peca_kgco2e"], "calculado")
        self.assertEqual(result.evidence_statuses["fonte_carbono_kgco2e_kg"], "declarado")

    def test_validate_dpp_publication_requires_impact_factor_sources(self):
        peca = SimpleNamespace(
            codigo="CAM-001",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-cam-001",
            tem_pais_fabricacao=True,
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            certificacoes=None,
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            fonte_agua_litros_kg=None,
            fonte_energia_kwh_kg=None,
            fonte_carbono_kgco2e_kg=None,
            metodologia_fatores_impacto=None,
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
            agua_peca_litros=25,
            energia_peca_kwh=2.5,
            pegada_carbono_kgco2e=0.5,
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertFalse(result.can_publish)
        self.assertIn("fonte do fator de agua obrigatoria para publicar DPP", result.errors)
        self.assertIn("fonte do fator de energia obrigatoria para publicar DPP", result.errors)
        self.assertIn("fonte do fator de carbono obrigatoria para publicar DPP", result.errors)

    def test_validate_dpp_publication_allows_missing_optional_calculated_indicator(self):
        peca = SimpleNamespace(
            codigo="CAM-001",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-cam-001",
            tem_pais_fabricacao=True,
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            certificacoes=None,
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            fonte_agua_litros_kg="Fator interno agua",
            fonte_energia_kwh_kg="Fator interno energia",
            fonte_carbono_kgco2e_kg="Fator interno carbono",
            agua_unit_source="L/kg",
            energia_unit_source="kWh/kg",
            metodologia_fatores_impacto="Estimativa calculada; nao substitui ACV oficial",
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
            agua_peca_litros=25,
            energia_peca_kwh=2.5,
            pegada_carbono_kgco2e=None,
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertTrue(result.can_publish)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.evidence_statuses["carbono_peca_kgco2e"], "ausente")

    def test_validate_dpp_publication_blocks_demo_factor_sources(self):
        peca = SimpleNamespace(
            codigo="CAM-001",
            nome="Camiseta Teste",
            gtin="7891234567890",
            dpp_uuid="uuid-cam-001",
            tem_pais_fabricacao=True,
            area_peca_m2=1,
            perda_corte_pct=20,
            lote_quantidade=100,
        )
        ficha = SimpleNamespace(
            composicao_fibras=json.dumps([{"fibra": "algodao", "pct": 100}]),
            certificacoes=None,
            gramatura_g_m2=200,
            agua_litros_kg=100,
            energia_kwh_kg=10,
            carbono_kgco2e_kg=2,
            fonte_agua_litros_kg="Proxy de demonstração PHYLLOS",
            fonte_energia_kwh_kg="Base setorial documentada - exemplo de teste",
            fonte_carbono_kgco2e_kg="Base setorial documentada - exemplo de teste",
            metodologia_fatores_impacto="Estimativa calculada; nao substitui ACV oficial",
            instrucoes_reparo="Lavar a frio",
            instrucoes_fim_de_vida="Encaminhar para reciclagem textil quando possivel",
            agua_peca_litros=25,
            energia_peca_kwh=2.5,
            pegada_carbono_kgco2e=0.5,
        )

        result = validate_dpp_publication(peca, ficha)

        self.assertFalse(result.can_publish)
        self.assertIn("fonte do fator de agua nao pode usar proxy de demonstracao para publicar DPP", result.errors)


if __name__ == "__main__":
    unittest.main()
