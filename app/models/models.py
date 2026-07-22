from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Colecao(Base):
    __tablename__ = "colecoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(Text)
    status = Column(String, default="planejamento")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    pecas = relationship("Peca", back_populates="colecao")


class Peca(Base):
    __tablename__ = "pecas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    colecao_id = Column(Integer, ForeignKey("colecoes.id"))
    status = Column(String, default="ideia")
    prioridade = Column(String, default="media")
    tecido = Column(String)
    custo_estimado = Column(Float)
    preco_sugerido = Column(Float)
    observacoes = Column(Text)
    prompt_croqui = Column(Text)
    prompt_foto = Column(Text)
    # DPP — Digital Product Passport
    gtin = Column(String, unique=True, nullable=True, index=True)
    dpp_uuid = Column(String, unique=True, nullable=True)
    dpp_status = Column(String, default="rascunho")  # rascunho | publicado | revogado
    area_peca_m2 = Column(Float)
    perda_corte_pct = Column(Float)
    lote_quantidade = Column(Integer)
    pais_fabricacao = Column(String)
    dpp_version = Column(String, default="1.0")
    data_publicacao = Column(DateTime(timezone=True))
    data_atualizacao = Column(DateTime(timezone=True), onupdate=func.now())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    colecao = relationship("Colecao", back_populates="pecas")
    ficha_tecnica = relationship("FichaTecnica", back_populates="peca", uselist=False)
    referencias_visuais = relationship("PecaVisualReference", back_populates="peca")
    etapas_producao = relationship("EtapaProducao", back_populates="peca")
    materiais = relationship("PecaMaterial", back_populates="peca", cascade="all, delete-orphan")
    modelagem_spec = relationship("ModelagemSpec", back_populates="peca", uselist=False)
    publicacoes_dpp = relationship("DppPublicationRecord", back_populates="peca")


class FichaTecnica(Base):
    __tablename__ = "fichas_tecnicas"

    id = Column(Integer, primary_key=True, index=True)
    peca_id = Column(Integer, ForeignKey("pecas.id"), unique=True)
    descricao_tecnica = Column(Text)
    materiais = Column(Text)
    construcao = Column(Text)
    medidas = Column(Text)
    qualidade = Column(Text)
    # DPP — campos estruturados para Digital Product Passport
    # JSON: [{"fibra": "poliester_reciclado", "pct": 78}, {"fibra": "elastano", "pct": 22}]
    composicao_fibras = Column(Text)
    instrucoes_reparo = Column(Text)
    instrucoes_fim_de_vida = Column(Text)
    # JSON: [{"nome": "OEKO-TEX", "numero": "XX-XXXXX", "validade": "2027-06-01"}]
    certificacoes = Column(Text)
    conteudo_reciclado_pct = Column(Float)
    pegada_carbono_kgco2e = Column(Float)
    gramatura_g_m2 = Column(Float)
    # Fatores ambientais — valores ja na unidade canonica (L/kg, kWh/kg, kg CO2e/kg)
    agua_litros_kg = Column(Float)
    energia_kwh_kg = Column(Float)
    carbono_kgco2e_kg = Column(Float)
    # Unidade original da fonte — obrigatoria para publicacao (ex: "m³/kg", "MJ/kg")
    agua_unit_source = Column(String)
    energia_unit_source = Column(String)
    fonte_agua_litros_kg = Column(Text)
    fonte_energia_kwh_kg = Column(Text)
    fonte_carbono_kgco2e_kg = Column(Text)
    metodologia_fatores_impacto = Column(Text)
    area_total_requerida_m2 = Column(Float)
    area_perdida_m2 = Column(Float)
    peso_peca_kg = Column(Float)
    agua_peca_litros = Column(Float)
    energia_peca_kwh = Column(Float)
    # Faixas de incerteza (opcionais — B3)
    agua_peca_incerteza_min = Column(Float)
    agua_peca_incerteza_max = Column(Float)
    carbono_peca_incerteza_min = Column(Float)
    carbono_peca_incerteza_max = Column(Float)
    evidencia_statuses = Column(Text)
    durabilidade_ciclos_lavagem = Column(Integer)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    peca = relationship("Peca", back_populates="ficha_tecnica")


class DppPublicationRecord(Base):
    """Registro append-only de cada execução do gate de publicação do DPP."""
    __tablename__ = "dpp_publication_records"

    id = Column(Integer, primary_key=True, index=True)
    peca_id = Column(Integer, ForeignKey("pecas.id"), nullable=False, index=True)
    dpp_uuid = Column(String, nullable=True, index=True)
    dpp_version = Column(String, nullable=False)
    gate_version = Column(String, nullable=False)
    resultado = Column(String, nullable=False)  # aprovado | bloqueado
    evidence_statuses = Column(Text, nullable=False)
    errors = Column(Text, nullable=False)
    warnings = Column(Text, nullable=False)
    snapshot_json = Column(Text)
    snapshot_sha256 = Column(String)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    peca = relationship("Peca", back_populates="publicacoes_dpp")


class UsageEvent(Base):
    """Evento de telemetria minimizado; não armazena conteúdo de campos."""
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False, index=True)
    schema_version = Column(String, nullable=False)
    session_id = Column(String, nullable=False, index=True)
    event_name = Column(String, nullable=False, index=True)
    page = Column(String, nullable=False, index=True)
    component = Column(String)
    action = Column(String)
    metadata_json = Column(Text, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EtapaProducao(Base):
    """Rastreabilidade por etapa da cadeia produtiva (Tier 1+)."""
    __tablename__ = "etapas_producao"

    id = Column(Integer, primary_key=True, index=True)
    peca_id = Column(Integer, ForeignKey("pecas.id"), nullable=False)
    # fiacao | tecelagem | corte | costura | tingimento | acabamento | lavanderia
    etapa = Column(String, nullable=False)
    pais = Column(String)
    instalacao_nome = Column(String)
    instalacao_gln = Column(String)  # Global Location Number (GS1)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    peca = relationship("Peca", back_populates="etapas_producao")


class VisualReference(Base):
    __tablename__ = "visual_references"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    titulo = Column(String, nullable=False)
    fonte = Column(String, nullable=False)
    source_url = Column(Text, nullable=False)
    image_url = Column(Text)
    categoria = Column(String, default="athleisure")
    contexto_uso = Column(Text, nullable=False)
    cenario = Column(Text, nullable=False)
    pecas_chave = Column(Text)
    paleta = Column(Text)
    styling_notes = Column(Text)
    atributos_visuais = Column(Text)
    prompt_tokens = Column(Text)
    prompt_negativo = Column(Text)
    direitos_uso = Column(Text, default="Referencia externa para curadoria. Nao copiar imagem para campanha ou produto final.")
    status = Column(String, default="prospectado")
    prioridade = Column(Integer, default=3)
    curador = Column(String, default="Codex")
    revisado_em = Column(String, nullable=False, server_default=func.current_date())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    pecas = relationship("PecaVisualReference", back_populates="referencia_visual")


class PecaVisualReference(Base):
    __tablename__ = "peca_visual_references"
    __table_args__ = (
        UniqueConstraint("peca_id", "visual_reference_id", "tipo_vinculo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    peca_id = Column(Integer, ForeignKey("pecas.id"), nullable=False)
    visual_reference_id = Column(Integer, ForeignKey("visual_references.id"), nullable=False)
    tipo_vinculo = Column(String, default="moodboard")
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    peca = relationship("Peca", back_populates="referencias_visuais")
    referencia_visual = relationship("VisualReference", back_populates="pecas")


# ---------------------------------------------------------------------------
# Catálogo de Fornecedores de Matérias-Primas
# ---------------------------------------------------------------------------

class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    # FOR-001, FOR-002 …
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    # cooperativa | industria | marca | distribuidor | projeto_agroecologico
    tipo = Column(String)
    estado = Column(String)
    cidade = Column(String)
    # JSON array: ["fibra","fiacao","tecido","malha","confeccao","produto_acabado"]
    elo_cadeia = Column(Text)
    produto_principal = Column(String)
    # amostra | pequeno_lote | medio_lote | industrial
    escala = Column(String)
    # b2b | b2c | cooperativas | marcas | exportacao (pode ser lista JSON)
    publico_alvo = Column(String)
    # confirmado | lead_validar | parceiro_estrategico
    status = Column(String, default="lead_validar")
    # 1–5 (ver critério no catálogo)
    nota_confianca = Column(Integer)
    # ISCM — conformidade trabalhista declarada/verificada
    # nao_verificado | em_processo | certificado_abvtex | certificado_sa8000
    conformidade_social = Column(String, default="nao_verificado")
    site = Column(String)
    email_contato = Column(String)
    telefone = Column(String)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    produtos = relationship("ProdutoFornecedor", back_populates="fornecedor", cascade="all, delete-orphan")
    certificacoes = relationship("CertificacaoFornecedor", back_populates="fornecedor", cascade="all, delete-orphan")


class ProdutoFornecedor(Base):
    __tablename__ = "produtos_fornecedor"

    id = Column(Integer, primary_key=True, index=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    nome = Column(String, nullable=False)
    codigo_fornecedor = Column(String)
    # pluma | fio | malha | tecido_plano | lona | produto_acabado
    tipo = Column(String)
    composicao = Column(String)
    cor = Column(String)
    # sem_tingimento | vegetal | convencional | natural
    tingimento = Column(String, default="sem_tingimento")
    gramatura_gm2 = Column(Float)
    largura_m = Column(Float)
    # pedido mínimo — string flexível: "100m", "200kg", "1 rolo"
    moq = Column(String)
    preco_referencia = Column(Float)
    # metro | kg | rolo | unidade
    unidade_preco = Column(String)
    uso_recomendado = Column(Text)
    risco = Column(Text)
    # sim | nao | a_validar
    disponivel = Column(String, default="a_validar")
    # scraping | manual | email | catalogo_pdf
    fonte = Column(String, default="manual")
    # ISCM — dado primário de consumo hídrico; L de água por kg de material produzido
    consumo_agua_litros_kg = Column(Float, nullable=True)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    fornecedor = relationship("Fornecedor", back_populates="produtos")
    usos_em_pecas = relationship("PecaMaterial", back_populates="produto")


class CertificacaoFornecedor(Base):
    __tablename__ = "certificacoes_fornecedor"

    id = Column(Integer, primary_key=True, index=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)
    # GOTS | OCS | IBD | ECOCERT | SisOrg | Participativa | USDA | EU_Organic
    tipo = Column(String, nullable=False)
    # sim | nao | pendente
    apresentado = Column(String, default="pendente")
    validade = Column(String)
    # fibra | fio | tecido | confeccao | produto_final
    escopo = Column(String)
    numero_licenca = Column(String)
    # URL, caminho de PDF, nota fiscal
    evidencia = Column(Text)
    # alto | medio | baixo
    nivel_confianca = Column(String)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    fornecedor = relationship("Fornecedor", back_populates="certificacoes")


class ModelagemSpec(Base):
    """MIE — Modelagem Intelligence Engine. Especificação técnica estruturada de modelagem.
    Cada registro é 1:1 com Peca. O campo status_revisao + notas_revisao alimenta o data moat."""
    __tablename__ = "modelagem_specs"

    id = Column(Integer, primary_key=True, index=True)
    peca_id = Column(Integer, ForeignKey("pecas.id"), unique=True, nullable=False)
    versao = Column(String, default="1.0")

    # Entrada em linguagem natural
    input_raw = Column(Text)
    intencoes = Column(Text)  # JSON: ["disfarcar_abdomen", "aumentar_conforto", ...]

    # Base de molde
    base_id = Column(String)        # "base_blusa_evase" | "base_calca_reta" | ...
    categoria_peca = Column(String) # blusa | calca | vestido | saia | macacao | ...
    silhueta = Column(String)       # reta | evase | ajustada | boxy | oversized | ...

    # Medidas corporais (cm)
    altura_cm = Column(Float)
    busto_cm = Column(Float)
    cintura_cm = Column(Float)
    quadril_cm = Column(Float)
    ombro_cm = Column(Float)
    costas_cm = Column(Float)
    cava_cm = Column(Float)
    braco_cm = Column(Float)
    punho_cm = Column(Float)
    gancho_cm = Column(Float)
    coxa_cm = Column(Float)
    joelho_cm = Column(Float)
    entreperna_cm = Column(Float)
    tornozelo_cm = Column(Float)
    comprimento_total_cm = Column(Float)

    # Folgas de vestibilidade (cm)
    folga_busto = Column(Float)
    folga_cintura = Column(Float)
    folga_quadril = Column(Float)
    folga_ombro = Column(Float)
    folga_cava = Column(Float)
    folga_coxa = Column(Float)
    folga_gancho = Column(Float)
    folga_entreperna = Column(Float)
    grau_ajuste = Column(String)  # fitted | semi | relaxed | oversized | compression

    # Construção — mecanismos 3D→2D
    mecanismos = Column(Text)           # JSON: ["pence_busto", "recorte_princesa", ...]
    linha_fio = Column(String)          # reto | trama | vies | misto
    tecidos_recomendados = Column(Text) # JSON: termos normalizados PLC
    tecidos_a_evitar = Column(Text)     # JSON: termos normalizados PLC

    # Comportamento de tecido
    elasticidade = Column(String)       # plano | 2vias | 4vias
    caimento = Column(String)           # fluido | estruturado | medio
    # medida_final = medida_corporal + folga - (medida_corporal * reducao_elastica_pct / 100)
    reducao_elastica_pct = Column(Float)

    # Graduação
    grade_base = Column(String)     # PP | P | M | G | GG | Plus
    regras_grading = Column(Text)   # JSON: incrementos por região e grade

    # Revisão humana — o coração do feedback loop / data moat
    # gerado | em_revisao | aprovado | reprovado
    status_revisao = Column(String, default="gerado")
    revisado_por = Column(String)
    revisado_em = Column(DateTime(timezone=True))
    notas_revisao = Column(Text)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    peca = relationship("Peca", back_populates="modelagem_spec")


class PecaMaterial(Base):
    """Vínculo entre uma peça e uma matéria-prima do catálogo de fornecedores."""
    __tablename__ = "peca_materiais"

    id = Column(Integer, primary_key=True, index=True)
    peca_id = Column(Integer, ForeignKey("pecas.id"), nullable=False)
    produto_fornecedor_id = Column(Integer, ForeignKey("produtos_fornecedor.id"), nullable=False)
    # principal | forro | ribana | aviamento | entretela | elastico
    funcao = Column(String, default="principal")
    # metros de tecido usados nesta peça (opcional — para cálculo de peso)
    quantidade_m = Column(Float, nullable=True)
    # peso em kg deste material na peça final (calculado ou informado)
    peso_kg = Column(Float, nullable=True)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    peca = relationship("Peca", back_populates="materiais")
    produto = relationship("ProdutoFornecedor", back_populates="usos_em_pecas")


# ---------------------------------------------------------------------------
# Banco de Modelagens — Pattern Library
# Fonte primária: Marlene Mukai, "Modelagem Prática para Confecção de Roupas
# em Tecido Plano", 3ª ed. 2015.
# ModelagemSpec (acima) é 1:1 com Peca; MoldeBase é a fonte canônica de
# padrões de corte referenciados por ModelagemSpec.base_id.
# ---------------------------------------------------------------------------

class MoldeBase(Base):
    """Catálogo de moldes base — padrões de corte reutilizáveis."""
    __tablename__ = "moldes_base"

    id = Column(Integer, primary_key=True, index=True)
    # ex: "base-saia-reta", "base-blusa-basica" — valor usado em ModelagemSpec.base_id
    codigo = Column(String, unique=True, nullable=False, index=True)
    nome = Column(String, nullable=False)
    # saia | blusa | calca | vestido | manga | camisa | casaco | infantil
    categoria = Column(String, nullable=False, index=True)
    # reta | lapis | gode | evase | basica | raglan | pantalona | ...
    subcategoria = Column(String)
    # mukai_2015 | outro
    fonte = Column(String, default="mukai_2015")
    # feminino | masculino | infantil | unissex
    genero = Column(String, default="feminino", index=True)
    # plano | malha | ambos
    tipo_tecido = Column(String, default="plano")
    descricao = Column(Text)
    # notas de construção: linhas de fio, número de partes, ordem de montagem
    notas_construcao = Column(Text)
    # referência à página no livro fonte
    pagina_fonte = Column(Integer)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    partes = relationship("MoldeParte", back_populates="molde_base", cascade="all, delete-orphan")
    derivacoes_origem = relationship(
        "MoldeDerivacao",
        foreign_keys="MoldeDerivacao.molde_origem_id",
        back_populates="molde_origem",
        cascade="all, delete-orphan",
    )
    derivacoes_destino = relationship(
        "MoldeDerivacao",
        foreign_keys="MoldeDerivacao.molde_derivado_id",
        back_populates="molde_derivado",
    )
    tecidos_indicados = relationship("TecidoIndicadoMolde", back_populates="molde_base", cascade="all, delete-orphan")
    variacoes = relationship("MoldeVariacao", back_populates="molde_base", cascade="all, delete-orphan")


class MoldeParte(Base):
    """Peça de molde dentro de um molde base (frente, costas, manga, cós, etc.)."""
    __tablename__ = "moldes_partes"

    id = Column(Integer, primary_key=True, index=True)
    molde_base_id = Column(Integer, ForeignKey("moldes_base.id"), nullable=False)
    # frente | costas | manga | gola | cos | bolso | carcela | punho | forro
    nome = Column(String, nullable=False)
    # marcações e pontos de referência: JSON com entalhes, pences, linhas de dobra
    marcacoes = Column(Text)
    # qty — número de partes a cortar (1 dobrado = 2 peças, ex: frente com pala)
    quantidade_corte = Column(Integer, default=1)
    observacoes = Column(Text)

    molde_base = relationship("MoldeBase", back_populates="partes")


class MoldeDerivacao(Base):
    """Relação de derivação entre moldes: base → variação com descrição da transformação."""
    __tablename__ = "moldes_derivacoes"
    __table_args__ = (
        UniqueConstraint("molde_origem_id", "molde_derivado_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    molde_origem_id = Column(Integer, ForeignKey("moldes_base.id"), nullable=False)
    molde_derivado_id = Column(Integer, ForeignKey("moldes_base.id"), nullable=False)
    # alargamento | encurtamento | pence | recorte | franzido | abertura | sobreposicao
    tipo_transformacao = Column(String)
    descricao = Column(Text)

    molde_origem = relationship("MoldeBase", foreign_keys=[molde_origem_id], back_populates="derivacoes_origem")
    molde_derivado = relationship("MoldeBase", foreign_keys=[molde_derivado_id], back_populates="derivacoes_destino")


class TabelaMedidasPadrao(Base):
    """Medidas corporais de referência por gênero, tipo de tecido, elasticidade e tamanho.
    Fonte primária: Mukai 2015. Um registro por (genero, tipo_tecido, elasticidade, tamanho, ponto_medida)."""
    __tablename__ = "tabela_medidas_padrao"
    __table_args__ = (
        UniqueConstraint("genero", "tipo_tecido", "elasticidade", "tamanho", "ponto_medida"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # feminino | masculino | infantil
    genero = Column(String, nullable=False, index=True)
    # plano | malha
    tipo_tecido = Column(String, nullable=False, index=True)
    # plano | baixa | media | alta  (elasticidade da malha; "plano" para tecido plano)
    elasticidade = Column(String, nullable=False, default="plano")
    # 36 | 38 | PP | P | M | G | GG | EGG | 2 | 4 | 6 (infantil por anos)
    tamanho = Column(String, nullable=False, index=True)
    # busto | cintura | quadril | ombro | costas | altura_corpo | largura_braco |
    # altura_cava | altura_busto | separacao_busto | comp_manga_comprida |
    # comp_manga_curta | punho_camisa | punho_blazer | altura_quadril |
    # altura_gancho | comp_joelho | comp_calca | largura_joelho | largura_tornozelo
    ponto_medida = Column(String, nullable=False, index=True)
    valor_cm = Column(Float, nullable=False)
    fonte = Column(String, default="mukai_2015")


class ReducaoMalha(Base):
    """Percentuais e valores de redução de medida por elasticidade do tecido.
    Mukai 2015, p.14. Aplicar antes de construir o molde para malha."""
    __tablename__ = "reducao_malha"
    __table_args__ = (
        UniqueConstraint("elasticidade", "ponto_medida"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # baixa | media | alta
    elasticidade = Column(String, nullable=False)
    ponto_medida = Column(String, nullable=False)
    # percentual de redução (quando a redução é proporcional à medida)
    reducao_pct = Column(Float, nullable=True)
    # redução absoluta em cm (quando é valor fixo independente da medida)
    reducao_cm = Column(Float, nullable=True)
    observacoes = Column(Text)


class TecidoIndicadoMolde(Base):
    """Tecidos indicados por molde base ou categoria de peça (Mukai 2015, p.8)."""
    __tablename__ = "tecidos_indicados_molde"

    id = Column(Integer, primary_key=True, index=True)
    # NULL quando a indicação é por categoria (não por molde específico)
    molde_base_id = Column(Integer, ForeignKey("moldes_base.id"), nullable=True)
    # usado quando molde_base_id é NULL — indicação geral por categoria
    categoria_peca = Column(String, nullable=True)
    nome_tecido = Column(String, nullable=False)
    # ideal | adequado | condicional | evitar
    adequacao = Column(String, default="ideal")
    observacoes = Column(Text)

    molde_base = relationship("MoldeBase", back_populates="tecidos_indicados")


class FolgaVestibilidade(Base):
    """Folgas de vestibilidade recomendadas por grau de ajuste e ponto de medida.
    A folga é adicionada após dividir a medida corporal por 4 (método Mukai)."""
    __tablename__ = "folgas_vestibilidade"
    __table_args__ = (
        UniqueConstraint("grau_ajuste", "categoria_peca", "ponto_medida"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # compression | fitted | semi | relaxed | oversized
    grau_ajuste = Column(String, nullable=False)
    # blusa | calca | vestido | saia | casaco (NULL = universal)
    categoria_peca = Column(String, nullable=True)
    # busto | cintura | quadril | cava | gancho
    ponto_medida = Column(String, nullable=False)
    # folga total em cm (dividida por 4 ao aplicar em 1/4 do molde)
    folga_total_cm = Column(Float, nullable=False)
    observacoes = Column(Text)


class MoldeVariacao(Base):
    """SKU de modelagem — combinação única e mensurável de molde base + tamanho + tecido + ajuste.
    Cada registro tem medidas de molde pré-calculadas e descrição em linguagem natural
    para matching semântico: descrição do usuário → SKU → base de medidas correta."""
    __tablename__ = "moldes_variacoes"
    __table_args__ = (
        UniqueConstraint("molde_base_id", "tamanho", "tipo_tecido", "elasticidade", "grau_ajuste"),
    )

    id = Column(Integer, primary_key=True, index=True)
    # ex: "saia-reta-40-plano-semi", "blusa-basica-M-malha-m-fitted"
    codigo = Column(String, unique=True, nullable=False, index=True)
    molde_base_id = Column(Integer, ForeignKey("moldes_base.id"), nullable=False)

    tamanho = Column(String, nullable=False, index=True)      # 36-62 plano | PP-EGG malha | 2-16 inf
    tipo_tecido = Column(String, nullable=False)               # plano | malha
    elasticidade = Column(String, nullable=False, default="plano")  # plano | baixa | media | alta
    # compression | fitted | semi | relaxed | oversized
    grau_ajuste = Column(String, nullable=False, index=True)
    genero = Column(String, nullable=False, default="feminino", index=True)

    # Variações de construção (preenchidas com padrão de cada categoria)
    # micro | curta | joelho | midi | longa | maxi | normal | cropped | comprida | bermuda | capri | 7_8
    comprimento = Column(String)
    # redondo | v | quadrado | barca | degage | colarinho | lapela | nenhum
    decote = Column(String)
    # sem_manga | curta | 3_4 | longa | raglan | japonesa | integrada | nenhum
    manga = Column(String)
    # zipper_lateral | zipper_traseiro | zipper_frente | botoes | elastico | amarracao | nenhum
    fechamento = Column(String)
    # alto | medio | baixo | elastico | nenhum
    cos = Column(String)

    # Medidas de molde pré-calculadas em cm
    # = medida_corporal (tabela_medidas_padrao) + folga_vestibilidade
    busto_molde        = Column(Float)
    cintura_molde      = Column(Float)
    quadril_molde      = Column(Float)
    ombro_molde        = Column(Float)
    costas_molde       = Column(Float)
    largura_braco_molde= Column(Float)
    altura_cava_molde  = Column(Float)
    comprimento_total_molde = Column(Float)
    gancho_molde       = Column(Float)
    largura_joelho_molde = Column(Float)
    largura_tornozelo_molde = Column(Float)

    # Semântica para matching de descrições em linguagem natural
    descricao_natural = Column(Text, nullable=False)
    # JSON: termos normalizados + sinônimos populares para busca vetorial / RAG
    tags = Column(Text)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    molde_base = relationship("MoldeBase", back_populates="variacoes")


# ---------------------------------------------------------------------------
# Impact Collector — banco de dados de impacto de matérias-primas
# Alimentado pelo módulo impact_collector/ a partir de fontes abertas.
# Sprint 2: SQLite local. Sprint 3: migra para Supabase Postgres.
# ---------------------------------------------------------------------------

class ImpactSource(Base):
    """Cada fonte consultada pelo pipeline de coleta."""
    __tablename__ = "impact_sources"

    id = Column(Integer, primary_key=True, index=True)
    # api | pdf | bulk_dump | scraping | oai_pmh | manual
    tipo = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    doi = Column(String, unique=True, nullable=True, index=True)
    url = Column(Text)
    titulo = Column(Text)
    autores = Column(Text)  # JSON array
    ano_publicacao = Column(Integer)
    journal = Column(String)
    acesso_aberto = Column(Boolean, default=True)
    licenca = Column(String)
    raw_storage_path = Column(Text)
    # coletado | parseado | extraido | validado | rejeitado
    status = Column(String, default="coletado")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    evidencias = relationship("ImpactEvidence", back_populates="source", cascade="all, delete-orphan")


class ImpactEvidence(Base):
    """Cada valor de impacto coletado de uma fonte específica."""
    __tablename__ = "impact_evidences"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("impact_sources.id"), nullable=False)
    fibra_id = Column(String, nullable=False, index=True)
    fingerprint = Column(String, unique=True, nullable=True, index=True)

    # Valores medidos
    co2eq_kg_por_kg = Column(Float)
    agua_l_por_kg = Column(Float)
    energia_mj_por_kg = Column(Float)

    # Metadados do estudo
    # cradle-to-gate | cradle-to-grave | gate-to-gate | outro
    escopo_lca = Column(String)
    metodologia_acv = Column(String)
    regiao_origem = Column(String)
    ano_referencia = Column(Integer)

    # Rastreabilidade
    pagina_referencia = Column(String)
    trecho_original = Column(Text)
    nota_curadoria = Column(Text)

    # Qualidade
    # alta | media | baixa
    confianca = Column(String, default="baixa")
    validado_humano = Column(Boolean, default=False)
    validado_em = Column(DateTime(timezone=True))
    validado_por = Column(String)

    # Extração
    # claude-haiku-4-5 | manual | regex
    extraction_model = Column(String)
    extraction_cost_usd = Column(Float)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    source = relationship("ImpactSource", back_populates="evidencias")


class ImpactMaterial(Base):
    """Valor agregado por fibra — calculado a partir das evidências coletadas."""
    __tablename__ = "impact_materials"

    id = Column(Integer, primary_key=True, index=True)
    fibra_id = Column(String, unique=True, nullable=False, index=True)
    nome_pt = Column(String, nullable=False)
    categoria = Column(String)  # natural_vegetal | sintetica_petroleo | mmcf | etc.
    aliases_json = Column(Text)  # JSON array de aliases

    # Valor agregado (mediana das evidências com confiança >= media)
    co2eq_kg_por_kg_agg = Column(Float)
    agua_l_por_kg_agg = Column(Float)
    energia_mj_por_kg_agg = Column(Float)

    # Ranges
    co2eq_range_min = Column(Float)
    co2eq_range_max = Column(Float)
    agua_range_min = Column(Float)
    agua_range_max = Column(Float)

    # Qualidade do agregado
    # alta | media | baixa
    confianca_agg = Column(String)
    n_evidencias = Column(Integer, default=0)
    regra_agregacao = Column(String)  # "mediana cradle-to-gate global"

    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
