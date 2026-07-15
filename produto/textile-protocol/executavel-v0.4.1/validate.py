#!/usr/bin/env python3
from pathlib import Path
import json, argparse, sys
from collections import Counter, defaultdict
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parent

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def schema_code(e):
    path=list(e.absolute_path)
    if path and path[0]=='assertions':
        if path[-1:] == ['evidence_status'] and e.validator=='const' and e.validator_value=='absent':
            return 'rule.assertion.inferred_no_evidence_elevation'
        if (path[-1:] == ['assertion_kind'] and e.validator=='const' and e.validator_value=='derived') or \
           (path[-1:] == ['derived_from_assertion_ids'] and e.validator=='minItems') or \
           (path[-1:] == ['method_version_id'] and e.validator in ['type','not']):
            return 'rule.assertion.calculated_requires_derivation_context'
    if e.validator=='required': return 'schema.required_field'
    if e.validator=='additionalProperties': return 'schema.additional_property'
    if path and path[0]=='publication_decisions' and path[-1]=='policy_version_id': return 'schema.publication_policy'
    return 'schema.validation_error'

def integrity(t):
    errs=[]
    for key in ['module_revisions','dimension_revisions','concept_revisions','commercial_name_revisions','fiber_concept_revisions']:
        ids=[x['id'] for x in t[key]]
        if len(ids)!=len(set(ids)): errs.append('integrity.duplicate_id:'+key)
    versions={x['id'] for x in t['taxonomy_versions']}
    modules={x['id'] for x in t['module_revisions']}; dims={x['id'] for x in t['dimension_revisions']}
    for x in t['module_revisions']:
        if x['part_of_version_id'] not in versions: errs.append('integrity.module_version_ref')
    for x in t['dimension_revisions']:
        if x['module_revision_id'] not in modules or x['part_of_version_id'] not in versions: errs.append('integrity.dimension_ref')
    for x in t['concept_revisions']:
        if x['dimension_revision_id'] not in dims or x['part_of_version_id'] not in versions: errs.append('integrity.concept_ref')
    return sorted(set(errs))

def semantic(doc,t):
    E=[]
    by=lambda arr:{x['id']:x for x in arr}
    actors=by(doc['actors']); evidence=by(doc['evidence']); methods=by(doc['methods']); models=by(doc['model_versions']); prompts=by(doc['prompt_versions']); cals=by(doc['calibration_versions']); execs=by(doc['executions']); assertions=by(doc['assertions']); reviews=by(doc['reviews']); pubs=by(doc['publication_decisions']); conflicts=by(doc['conflicts']); measurements=by(doc['measurements']); comps=by(doc['composition_components']); finishes=by(doc['finish_applications'])
    dimdefs=by(t['dimension_revisions']); concepts=by(t['concept_revisions']); cnames=by(t['commercial_name_revisions']); benchmark=t['benchmark_versions'][0]
    # general references and decision link
    for a in assertions.values():
        if a['dimension_revision_id'] not in dimdefs: E.append('semantic.unknown_dimension_revision')
        p=pubs.get(a['publication_decision_id'])
        if not p: E.append('semantic.missing_publication_decision')
        elif p['assertion_id']!=a['id']: E.append('semantic.publication_assertion_mismatch')
        for eid in a['evidence_ids']:
            if eid not in evidence: E.append('semantic.unknown_evidence')
        if a['method_version_id'] and a['method_version_id'] not in methods: E.append('semantic.unknown_method')
        for rid in a['review_ids']:
            if rid not in reviews: E.append('semantic.unknown_review')
        v=a['value']
        if 'concept_revision_id' in v and v['concept_revision_id'] not in concepts: E.append('semantic.unknown_concept_revision')
        if 'declared_function_revision_id' in v and v['declared_function_revision_id'] not in concepts: E.append('semantic.unknown_concept_revision')
        if 'commercial_name_revision_id' in v and v['commercial_name_revision_id'] not in cnames: E.append('semantic.unknown_commercial_name_revision')
        if 'measurement_id' in v and v['measurement_id'] not in measurements: E.append('semantic.unknown_measurement')
        if 'composition_component_id' in v and v['composition_component_id'] not in comps: E.append('semantic.unknown_composition_component')
        if 'finish_application_id' in v and v['finish_application_id'] not in finishes: E.append('semantic.unknown_finish_application')
        # inference
        if a['assertion_kind']=='inferred':
            if a['evidence_status'] != 'absent': E.append('rule.assertion.inferred_no_evidence_elevation')
            if not a['execution_id'] or a['execution_id'] not in execs: E.append('rule.assertion.inferred_requires_execution')
            else:
                x=execs[a['execution_id']]
                if a['id'] not in x['produced_assertion_ids']: E.append('rule.assertion.inferred_requires_execution')
                if not set(a['evidence_ids']).issubset(set(x['consumed_evidence_ids'])): E.append('rule.assertion.inferred_requires_execution')
        # calculated is reserved for deterministic, reproducible derivations
        if a['evidence_status']=='calculated' and a['assertion_kind']!='inferred':
            if a['assertion_kind']!='derived' or not a['method_version_id'] or not a['derived_from_assertion_ids']:
                E.append('rule.assertion.calculated_requires_derivation_context')
            else:
                if a['method_version_id'] not in methods:
                    E.append('rule.assertion.calculated_requires_derivation_context')
                if any(source_id not in assertions for source_id in a['derived_from_assertion_ids']):
                    E.append('rule.assertion.calculated_requires_derivation_context')
        # probability calibration
        if a['probability'] is not None:
            if not a['confidence_is_calibrated'] or not a['calibration_version_id'] or a['calibration_version_id'] not in cals: E.append('rule.assertion.probability_requires_calibration')
        if a['confidence_is_calibrated'] and (not a['calibration_version_id'] or a['calibration_version_id'] not in cals): E.append('rule.assertion.probability_requires_calibration')
        # verified requirements
        if a['evidence_status']=='verified':
            good_ev=any(evidence.get(eid,{}).get('acceptance_status')=='accepted' and evidence.get(eid,{}).get('evidentiary_relevance')=='sufficient' for eid in a['evidence_ids'])
            m=methods.get(a['method_version_id']) if a['method_version_id'] else None
            method_ok=bool(m and m['verification_status']=='verified' and a['dimension_revision_id'] in m['applicable_dimension_revision_ids'])
            human_review=False
            for rid in a['review_ids']:
                r=reviews.get(rid); actor=actors.get(r.get('performed_by_actor_id')) if r else None
                if r and r['outcome']=='accepted' and actor and actor['actor_type']=='human': human_review=True
            if not (good_ev and method_ok and human_review): E.append('rule.assertion.verified_requirements')
    # execution refs
    for x in execs.values():
        if x['model_version_id'] not in models: E.append('semantic.execution_unknown_model')
        if x['prompt_version_id'] not in prompts: E.append('semantic.execution_unknown_prompt')
        if x['executed_by_actor_id'] not in actors: E.append('semantic.execution_unknown_actor')
        if x['calibration_version_id'] and x['calibration_version_id'] not in cals: E.append('semantic.execution_unknown_calibration')
        for eid in x['consumed_evidence_ids']:
            if eid not in evidence: E.append('semantic.execution_unknown_evidence')
    # publication policies and v0.4 rules
    for p in pubs.values():
        if p['assertion_id'] not in assertions: E.append('semantic.publication_assertion_mismatch')
        if p['decided_by_actor_id'] not in actors: E.append('semantic.publication_unknown_actor')
    high={x['id'] for x in t['commercial_name_revisions'] if x['ambiguity_level']=='high'}
    open_assertions=set()
    for c in conflicts.values():
        if c['status']=='open': open_assertions.update(c['assertion_ids'])
        for aid in c['assertion_ids']:
            if aid not in assertions: E.append('semantic.conflict_unknown_assertion')
    for a in assertions.values():
        p=pubs.get(a['publication_decision_id'],{})
        did=a['dimension_revision_id']; v=a['value']
        if did.endswith('composition.status:v0.3') and a['assertion_kind']=='inferred' and p.get('outcome')!='withhold': E.append('rule.publication.composition_inferred_withhold')
        if did.endswith('finishing.declared_function:v0.3'):
            missing=(not a['evidence_ids'] or not a['method_version_id'])
            if missing and p.get('outcome')!='withhold': E.append('rule.publication.function_missing_context_withhold')
        if a['capture_quality']=='insufficient' and p.get('outcome')!='request_more_evidence': E.append('rule.publication.capture_insufficient_request')
        if v.get('concept_revision_id','').endswith('capture.quality.insufficient:v0.3') and p.get('outcome')!='request_more_evidence': E.append('rule.publication.capture_insufficient_request')
        if v.get('commercial_name_revision_id') in high and p.get('outcome')!='request_more_evidence': E.append('rule.publication.commercial_high_ambiguity_request')
        if a['id'] in open_assertions and p.get('outcome') not in ['withhold','request_more_evidence']: E.append('rule.publication.open_conflict_block')
        if did.endswith('tactile.hand:v0.3') and a['evidence_ids'] and all(evidence.get(e,{}).get('evidence_type')=='image' for e in a['evidence_ids']): E.append('rule.tactile.no_image_only')
    # specialized objects exactly referenced
    refs=Counter()
    for a in assertions.values():
        for k in ['measurement_id','composition_component_id','finish_application_id']:
            if k in a['value']: refs[a['value'][k]]+=1
    for oid in list(measurements)+list(comps)+list(finishes):
        if refs[oid]!=1: E.append('rule.specialized_value.through_assertion')
    # measurement context and unit compatibility
    mt={x['id']:x for x in t['measurement_types']}
    for m in measurements.values():
        if m.get('method_version_id') not in methods: E.append('semantic.measurement_unknown_method')
        if m.get('measurement_type_id') in mt and m.get('unit_id') is not None and m.get('unit_id') not in mt[m['measurement_type_id']]['allowed_unit_ids']: E.append('semantic.measurement_unit_incompatible')
    # cardinality active
    count=defaultdict(int)
    for a in assertions.values():
        p=pubs.get(a['publication_decision_id'],{})
        if a['status']=='active' and a['id'] not in open_assertions and p.get('outcome') in ['publish','publish_with_status']:
            count[a['dimension_revision_id']]+=1
    for did,n in count.items():
        if did in dimdefs and dimdefs[did]['cardinality']=='one' and n>1: E.append('rule.cardinality.dimension')
    # correction & supersedes
    superseders=defaultdict(list)
    for a in assertions.values():
        if a['supersedes_assertion_id']:
            superseders[a['supersedes_assertion_id']].append(a['id'])
            target=assertions.get(a['supersedes_assertion_id'])
            if not target or target['status']!='superseded': E.append('rule.history.supersedes_preserves_old')
    for r in reviews.values():
        if r['outcome']=='corrected' and not superseders.get(r['assertion_id']): E.append('rule.history.correction_requires_replacement')
    # benchmark
    bd=doc['benchmark_decision']; allowed_d=set(benchmark['allowed_dimension_revision_ids']); allowed_c=set(benchmark['allowed_concept_revision_ids'])
    for aid in bd['based_on_assertion_ids']:
        a=assertions.get(aid)
        if not a: E.append('semantic.benchmark_unknown_assertion'); continue
        cid=a['value'].get('concept_revision_id')
        if a['dimension_revision_id'] not in allowed_d or (cid and cid not in allowed_c): E.append('rule.benchmark.versioned_capability')
    insufficient=any(a['capture_quality']=='insufficient' or a['value'].get('concept_revision_id','').endswith('capture.quality.insufficient:v0.3') for a in assertions.values())
    if insufficient and bd['outcome']!='request_new_evidence': E.append('rule.publication.capture_insufficient_request')
    return sorted(set(E))

def validate(path,schema,tax):
    doc=load(path); v=Draft202012Validator(schema,format_checker=FormatChecker()); errs=[]
    for e in sorted(v.iter_errors(doc),key=lambda x:list(x.absolute_path)):
        code=schema_code(e)
        if code.startswith('rule.'):
            errs.append(code)
        else:
            errs.append(f'{code}: {".".join(map(str,e.absolute_path)) or "$"}: {e.message}')
    errs+=semantic(doc,tax)
    return doc,sorted(set(errs))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('paths',nargs='*'); ap.add_argument('--all',action='store_true'); args=ap.parse_args()
    schema=load(ROOT/'taxonomia-textil-v0.3.schema.json'); tax=load(ROOT/'taxonomia-textil-v0.3.json')
    Draft202012Validator.check_schema(schema)
    ie=integrity(tax)
    if ie:
        print('FAIL taxonomy integrity'); [print(' -',x) for x in ie]; return 1
    print('PASS taxonomy dictionary integrity')
    print('PASS JSON Schema Draft 2020-12 meta-validation')
    paths=[Path(x) for x in args.paths]
    if args.all or not paths: paths=sorted((ROOT/'fixtures'/'validas').glob('*.json'))+sorted((ROOT/'fixtures'/'invalidas').glob('*.json'))
    fails=0
    for p in paths:
        doc,errs=validate(p,schema,tax); t=doc.get('_test',{}); actual='valid' if not errs else 'invalid'; exp=t.get('expected_result','valid'); rule=t.get('expected_rule'); ok=actual==exp and (not rule or any(rule in e for e in errs)); print(('PASS' if ok else 'FAIL'),p, f'expected={exp} actual={actual}', f'expected_rule={rule}' if rule else '')
        for e in errs: print(' -',e)
        if not ok: fails+=1
    return fails
if __name__=='__main__': sys.exit(main())
