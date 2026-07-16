# PHYLLOS Environmental Data v0.3

Pacote de auditoria, schema e validação para perfis ambientais de amostras têxteis.

## Status de uso

Aprovado para auditoria, revisão humana, coleta e implementação estrutural. Não autorizado para cálculo ambiental oficial, publicação de impactos ou alegações ambientais.

Os sete casos com composição percentual e gramatura permanecem provisórios: `calculability_review_status = pending_human_review` e `calculations = []`.

## Instalação em ambiente limpo

```bash
python -m venv .venv
. .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m unittest -v test_environmental_profile_v0_3.py
```

## Validação de um perfil

```bash
python validate_environmental_profile_v0_3.py perfil.json
```

O processo executa primeiro o JSON Schema Draft 2020-12 e depois as regras semânticas de unicidade e integridade referencial.
