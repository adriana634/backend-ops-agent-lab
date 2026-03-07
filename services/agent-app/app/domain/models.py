from dataclasses import dataclass

@dataclass(frozen=True)
class Incident:
    incident_id: str
    service: str
    severity: str
    summary: str
    status: str


@dataclass(frozen=True)
class InvestigationResult:
    incident_id: str
    diagnosis: str
