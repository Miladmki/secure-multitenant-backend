# # app/services/audit_logger.py

# from sqlalchemy.orm import Session
# from app.models.audit_log import BusinessAuditLog


# class BusinessAuditLogger:
#     def __init__(self, db: Session):
#         self.db = db

#     def log(
#         self,
#         *,
#         user_id: int | None,
#         tenant_id: int | None,
#         action: str,
#         resource: str,
#         metadata: dict | None = None,
#     ) -> None:
#         entry = BusinessAuditLog(
#             user_id=user_id,
#             tenant_id=tenant_id,
#             action=action,
#             resource=resource,
#             metadata=metadata or {},
#         )

#         self.db.add(entry)
#         self.db.commit()
