# Taxonomia têxtil v0.1

## Princípio

A taxonomia separa estrutura física, construção, atributos aparentes, propriedades mensuradas, composição, nome comercial e acabamento. Similaridade visual não confirma composição nem denominação comercial.

## Família estrutural

- `tecido_plano`
- `malha_trama`
- `malha_urdume`
- `nao_tecido`
- `estrutura_composta`
- `indeterminado`

Não usar a pergunta “tecido ou malha”. A forma correta é “tecido plano, malha, não tecido ou indeterminado”.

## Construção primária

Para tecido plano:

- `tafeta`
- `sarja`
- `cetim`
- `indeterminado`

Para malha de trama:

- `jersey`
- `ribana_canelada`
- `interlock`
- `purl_links_links`
- `indeterminado`

Para malha de urdume:

- `tricot`
- `raschel`
- `indeterminado`

Detalhes de não tecidos permanecem no backlog até revisão especializada e dataset adequado.

## Derivação, padrão ou mecanismo

- `cestaria_panama_basket`
- `oxford`
- `ripstop`
- `espinha_de_peixe`
- `broken_twill`
- `dobby`
- `jacquard`
- `felpa_ou_pelo`
- `dupla_face_dupla_camada`
- `indeterminado`

`Dobby` e `jacquard` não são ligamentos-base equivalentes a tafetá, sarja e cetim.

## Atributos visuais

Toda saída proveniente de imagem usa o qualificador “aparente”.

| Atributo | Valores v0 |
|---|---|
| Transparência | `opaco`, `semiopaco`, `semitransparente`, `transparente`, `indeterminado` |
| Brilho | `fosco`, `semifosco`, `acetinado`, `brilhante`, `indeterminado` |
| Textura | `lisa`, `granulada`, `canelada`, `felpuda`, `aveludada`, `slub_aparente`, `indeterminado` |
| Regularidade | `regular`, `irregular`, `indeterminado` |

## Propriedades mensuráveis

- gramatura em `g/m²`;
- densidade em `fios/cm`, `carreiras/cm` ou `colunas/cm`;
- espessura em `mm`;
- largura útil em `cm`;
- alongamento e recuperação em `%`, por direção e método;
- caimento por método definido;
- absorção ou tempo de molhamento por protocolo.

Essas propriedades não recebem valor numérico a partir de fotografia comum.

## Composição

A composição é uma lista de fibras normalizadas, percentuais e fonte. Hipóteses de fibra ficam em conjunto separado e não preenchem este campo.

Estados operacionais:

- `composicao_ausente`
- `composicao_parcial_nao_publicavel`
- `composicao_completa`

## Nome comercial

O nome comercial permanece separado. Exemplos: denim, chambray, cambraia, voile e organza.

- Chambray clássico é normalmente tafetá, com urdume colorido e trama clara.
- Denim é normalmente sarja, com urdume colorido ou índigo e trama clara.
- Sarja, denim e chambray não pertencem ao mesmo nível taxonômico.

## Acabamento

Vocabulário documental inicial:

- `mercerizado`
- `calandrado`
- `sanforizado`
- `escovado`
- `lixado`
- `peletizado`
- `resinado`
- `revestido`
- `impermeabilizado`
- `repelente`
- `antimicrobiano`
- `anti_chama`
- `outro`
- `nao_informado`

Acabamento funcional não é confirmado pela aparência.

## Escopo congelado para o primeiro benchmark

O primeiro benchmark cobre somente:

1. família estrutural;
2. tafetá, sarja e cetim em tecido plano;
3. transparência aparente;
4. qualidade da captura;
5. decisão `classificar / abster / pedir nova evidência`.
