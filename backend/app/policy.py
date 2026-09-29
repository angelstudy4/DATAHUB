from dataclasses import dataclass

@dataclass
class PolicyResult:
    decision: str
    reason: str

def evaluate(permission: str, permissions: list[str], risk: str="normal") -> PolicyResult:
    if permission not in permissions:
        return PolicyResult("deny", "missing_permission")
    if risk == "critical":
        return PolicyResult("review", "critical_risk_requires_approval")
    return PolicyResult("allow", "policy_satisfied")
