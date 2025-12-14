from typing import List, Dict


def evaluate_evidence(answer_text: str, evidence_terms: List[str]) -> Dict[str, object]:
    hits = [term for term in evidence_terms if term in answer_text]
    total = len(evidence_terms)
    hit_count = len(hits)

    return {
        "evidence_terms": evidence_terms,
        "hits": hits,
        "hit_count": hit_count,
        "total": total,
        "hit_rate": f"{hit_count} / {total}",
    }
