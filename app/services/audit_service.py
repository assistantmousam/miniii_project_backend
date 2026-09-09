from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    admin_id,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:

    audit_log = AuditLog(
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )

    db.add(audit_log)
    db.flush()

    return audit_log