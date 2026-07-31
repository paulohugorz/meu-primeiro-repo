import json
from collections import defaultdict
from .schemas import ConflictReport, DecisionAction, EvidenceAssertion

def detect_conflicts(assertions: list[EvidenceAssertion]) -> ConflictReport:
    grouped=defaultdict(list)
    for item in assertions:
        if item.verified or item.confidence >= .5: grouped[item.field_name].append(item)
    fields=[]; ids=[]
    for field, items in grouped.items():
        values={json.dumps(item.value, ensure_ascii=False, sort_keys=True) for item in items}
        if len(values)>1:
            fields.append(field); ids.extend(item.assertion_id for item in items)
    return ConflictReport(conflict_detected=bool(fields), fields=sorted(fields),
        action=DecisionAction.ESCALATE_CONFLICT if fields else DecisionAction.SHADOW,
        assertion_ids=sorted(ids))
