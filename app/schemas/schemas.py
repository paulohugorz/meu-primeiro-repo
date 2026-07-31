from pydantic import BaseModel, Field
from typing import Any, Optional, List
from datetime import datetime


class ColecaoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    status: Optional[str] = "planejamento"


class ColecaoCreate(ColecaoBase):
    pass


class ColecaoOut(ColecaoBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class PecaBase(BaseModel):
    codigo: str
    nome: str
    colecao_id: Optional[int] = None
    status: Optional[str] = "ideia"
    prioridade: Optional[str] = "media"
    tecido: Optional[str] = None
    custo_estimado: Optional[float] = None
    preco_sugerido: Optional[float] = None
    observacoes: Optional[str] = None
    prompt_croqui: Optional[str] = None
    prompt_foto: Optional[str] = None
    gtin: Optional[str] = None
    dpp_uuid: Optional[str] = None
    dpp_status: Optional[str] = "rascunho"
    area_peca_m2: Optional[float] = None
    perda_corte_pct: Optional[float] = None
    lote_quantidade: Optional[int] = None
    pais_fabricacao: Optional[str] = None
    dpp_version: Optional[str] = "1.0"
    data_publicacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None


class PecaCreate(PecaBase):
    pass


class PecaUpdate(BaseModel):
    nome: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    tecido: Optional[str] = None
    custo_estimado: Optional[float] = None
    preco_sugerido: Optional[float] = None
    observacoes: Optional[str] = None
    prompt_croqui: Optional[str] = None
    prompt_foto: Optional[str] = None
    gtin: Optional[str] = None
    dpp_uuid: Optional[str] = None
    dpp_status: Optional[str] = None
    area_peca_m2: Optional[float] = None
    perda_corte_pct: Optional[float] = None
    lote_quantidade: Optional[int] = None
    pais_fabricacao: Optional[str] = None
    dpp_version: Optional[str] = None
    data_publicacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None


class PecaOut(PecaBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class FichaTecnicaBase(BaseModel):
    descricao_tecnica: Optional[str] = None
    materiais: Optional[str] = None
    construcao: Optional[str] = None
    medidas: Optional[str] = None
    qualidade: Optional[str] = None
    # DPP
    composicao_fibras: Optional[str] = None       # JSON string
    instrucoes_reparo: Optional[str] = None
    instrucoes_fim_de_vida: Optional[str] = None
    certificacoes: Optional[str] = None            # JSON string
    conteudo_reciclado_pct: Optional[float] = None
    pegada_carbono_kgco2e: Optional[float] = None
    gramatura_g_m2: Optional[float] = None
    agua_litros_kg: Optional[float] = None
    energia_kwh_kg: Optional[float] = None
    carbono_kgco2e_kg: Optional[float] = None
    fonte_agua_litros_kg: Optional[str] = None
    fonte_energia_kwh_kg: Optional[str] = None
    fonte_carbono_kgco2e_kg: Optional[str] = None
    metodologia_fatores_impacto: Optional[str] = None
    area_total_requerida_m2: Optional[float] = None
    area_perdida_m2: Optional[float] = None
    peso_peca_kg: Optional[float] = None
    agua_peca_litros: Optional[float] = None
    energia_peca_kwh: Optional[float] = None
    evidencia_statuses: Optional[str] = None
    durabilidade_ciclos_lavagem: Optional[int] = None


class FichaTecnicaCreate(FichaTecnicaBase):
    peca_id: int


class FichaTecnicaOut(FichaTecnicaBase):
    id: int
    peca_id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class EtapaProducaoBase(BaseModel):
    etapa: str
    pais: Optional[str] = None
    instalacao_nome: Optional[str] = None
    instalacao_gln: Optional[str] = None


class EtapaProducaoCreate(EtapaProducaoBase):
    peca_id: int


class EtapaProducaoOut(EtapaProducaoBase):
    id: int
    peca_id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class VisualReferenceBase(BaseModel):
    slug: str
    titulo: str
    fonte: str
    source_url: str
    image_url: Optional[str] = None
    categoria: Optional[str] = "athleisure"
    contexto_uso: str
    cenario: str
    pecas_chave: Optional[str] = None
    paleta: Optional[str] = None
    styling_notes: Optional[str] = None
    atributos_visuais: Optional[str] = None
    prompt_tokens: Optional[str] = None
    prompt_negativo: Optional[str] = None
    direitos_uso: Optional[str] = "Referencia externa para curadoria. Nao copiar imagem para campanha ou produto final."
    status: Optional[str] = "prospectado"
    prioridade: Optional[int] = 3
    curador: Optional[str] = "Codex"
    revisado_em: Optional[str] = None


class VisualReferenceCreate(VisualReferenceBase):
    pass


class VisualReferenceOut(VisualReferenceBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class PecaVisualReferenceCreate(BaseModel):
    visual_reference_id: int
    tipo_vinculo: Optional[str] = "moodboard"
    observacoes: Optional[str] = None


class PecaVisualReferenceOut(PecaVisualReferenceCreate):
    id: int
    peca_id: int
    criado_em: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Catálogo de Fornecedores
# ---------------------------------------------------------------------------

class CertificacaoFornecedorCreate(BaseModel):
    tipo: str
    apresentado: Optional[str] = "pendente"
    validade: Optional[str] = None
    escopo: Optional[str] = None
    numero_licenca: Optional[str] = None
    evidencia: Optional[str] = None
    nivel_confianca: Optional[str] = None


class CertificacaoFornecedorOut(CertificacaoFornecedorCreate):
    id: int
    fornecedor_id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class ProdutoFornecedorCreate(BaseModel):
    nome: str
    codigo_fornecedor: Optional[str] = None
    tipo: Optional[str] = None
    composicao: Optional[str] = None
    cor: Optional[str] = None
    tingimento: Optional[str] = "sem_tingimento"
    gramatura_gm2: Optional[float] = None
    largura_m: Optional[float] = None
    moq: Optional[str] = None
    preco_referencia: Optional[float] = None
    unidade_preco: Optional[str] = None
    uso_recomendado: Optional[str] = None
    risco: Optional[str] = None
    disponivel: Optional[str] = "a_validar"
    fonte: Optional[str] = "manual"
    consumo_agua_litros_kg: Optional[float] = None
    observacoes: Optional[str] = None


class ProdutoFornecedorOut(ProdutoFornecedorCreate):
    id: int
    fornecedor_id: int
    criado_em: datetime

    class Config:
        from_attributes = True


class FornecedorCreate(BaseModel):
    codigo: str
    nome: str
    tipo: Optional[str] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    elo_cadeia: Optional[str] = None
    produto_principal: Optional[str] = None
    escala: Optional[str] = None
    publico_alvo: Optional[str] = None
    status: Optional[str] = "lead_validar"
    nota_confianca: Optional[int] = None
    conformidade_social: Optional[str] = "nao_verificado"
    site: Optional[str] = None
    email_contato: Optional[str] = None
    telefone: Optional[str] = None
    observacoes: Optional[str] = None


class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    elo_cadeia: Optional[str] = None
    produto_principal: Optional[str] = None
    escala: Optional[str] = None
    publico_alvo: Optional[str] = None
    status: Optional[str] = None
    nota_confianca: Optional[int] = None
    conformidade_social: Optional[str] = None
    site: Optional[str] = None
    email_contato: Optional[str] = None
    telefone: Optional[str] = None
    observacoes: Optional[str] = None


class FornecedorOut(FornecedorCreate):
    id: int
    criado_em: datetime
    produtos: List[ProdutoFornecedorOut] = []
    certificacoes: List[CertificacaoFornecedorOut] = []

    class Config:
        from_attributes = True


# Resultado de busca no catálogo de matérias-primas (produto + fornecedor juntos)
class MateriaPrimaOut(BaseModel):
    id: int
    nome: str
    codigo_fornecedor: Optional[str] = None
    tipo: Optional[str] = None
    composicao: Optional[str] = None
    tingimento: Optional[str] = None
    gramatura_gm2: Optional[float] = None
    largura_m: Optional[float] = None
    moq: Optional[str] = None
    preco_referencia: Optional[float] = None
    unidade_preco: Optional[str] = None
    uso_recomendado: Optional[str] = None
    disponivel: Optional[str] = None
    consumo_agua_litros_kg: Optional[float] = None
    fornecedor_id: int
    fornecedor_nome: str
    fornecedor_cidade: Optional[str] = None
    nota_confianca: Optional[int] = None
    certificacoes_fornecedor: List[CertificacaoFornecedorOut] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# ISCM — Índice de Sustentabilidade da Cadeia de Moda
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# MIE — Modelagem Intelligence Engine
# ---------------------------------------------------------------------------

class ModelagemSpecBase(BaseModel):
    versao: Optional[str] = "1.0"
    input_raw: Optional[str] = None
    intencoes: Optional[str] = None           # JSON string
    base_id: Optional[str] = None
    categoria_peca: Optional[str] = None
    silhueta: Optional[str] = None
    # medidas corporais
    altura_cm: Optional[float] = None
    busto_cm: Optional[float] = None
    cintura_cm: Optional[float] = None
    quadril_cm: Optional[float] = None
    ombro_cm: Optional[float] = None
    costas_cm: Optional[float] = None
    cava_cm: Optional[float] = None
    braco_cm: Optional[float] = None
    punho_cm: Optional[float] = None
    gancho_cm: Optional[float] = None
    coxa_cm: Optional[float] = None
    joelho_cm: Optional[float] = None
    entreperna_cm: Optional[float] = None
    tornozelo_cm: Optional[float] = None
    comprimento_total_cm: Optional[float] = None
    # folgas
    folga_busto: Optional[float] = None
    folga_cintura: Optional[float] = None
    folga_quadril: Optional[float] = None
    folga_ombro: Optional[float] = None
    folga_cava: Optional[float] = None
    folga_coxa: Optional[float] = None
    folga_gancho: Optional[float] = None
    folga_entreperna: Optional[float] = None
    grau_ajuste: Optional[str] = None
    # construção
    mecanismos: Optional[str] = None
    linha_fio: Optional[str] = None
    tecidos_recomendados: Optional[str] = None
    tecidos_a_evitar: Optional[str] = None
    # tecido
    elasticidade: Optional[str] = None
    caimento: Optional[str] = None
    reducao_elastica_pct: Optional[float] = None
    # graduação
    grade_base: Optional[str] = None
    regras_grading: Optional[str] = None


class ModelagemSpecCreate(ModelagemSpecBase):
    peca_id: int


class ModelagemSpecUpdate(ModelagemSpecBase):
    pass


class ModelagemSpecRevisao(BaseModel):
    """Payload exclusivo para o loop de feedback — revisão humana."""
    status_revisao: str  # gerado | em_revisao | aprovado | reprovado
    revisado_por: Optional[str] = None
    notas_revisao: Optional[str] = None


class ModelagemSpecOut(ModelagemSpecBase):
    id: int
    peca_id: int
    status_revisao: str
    revisado_por: Optional[str] = None
    revisado_em: Optional[datetime] = None
    notas_revisao: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class ISCMDimensaoOut(BaseModel):
    pontos: float
    peso: float
    fonte: str              # primario | estimado | ausente
    metodologia: str
    referencias: List[str] = []
    indicador_auditavel: Optional[str] = None


class ISCMOut(BaseModel):
    legacy_status: str = "experimental_legacy"
    disclaimer: str = "Compatibilidade apenas; não é indicador oficial nem resultado calibrado."
    peca_codigo: str
    score_total: float
    nivel: str              # insuficiente | basico | intermediario | avancado | referencia
    dimensoes: dict         # chave → ISCMDimensaoOut serializado
    cobertura_dados_pct: float
    alertas: List[str] = []


class PecaMaterialCreate(BaseModel):
    produto_fornecedor_id: int
    # principal | forro | ribana | aviamento | entretela | elastico
    funcao: Optional[str] = "principal"
    # metros de tecido usados nesta peça (opcional)
    quantidade_m: Optional[float] = None
    # peso em kg na peça final — se omitido, calculado de quantidade_m × gramatura × largura
    peso_kg: Optional[float] = None
    observacoes: Optional[str] = None


class PecaMaterialOut(BaseModel):
    id: int
    peca_id: int
    produto_fornecedor_id: int
    funcao: Optional[str] = None
    quantidade_m: Optional[float] = None
    peso_kg: Optional[float] = None
    observacoes: Optional[str] = None
    criado_em: datetime
    produto: MateriaPrimaOut

    class Config:
        from_attributes = True


class UsageEventCreate(BaseModel):
    event_id: str
    schema_version: str = "usage-event-v2"
    session_id: str
    event_name: str
    page: str
    component: Optional[str] = None
    action: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime
    event_version: int = 1
    anonymous_id: Optional[str] = None
    user_id_hash: Optional[str] = None
    workspace_id_hash: Optional[str] = None
    source: str = "web"
    environment: str = "production"
    application_version: Optional[str] = None
    request_id: Optional[str] = None
