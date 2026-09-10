import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.admin_security import get_current_admin
from app.db.database import get_db
from app.models.user import User
from app.services.analytics_service import (
    get_admin_analytics,
)


router = APIRouter(
    prefix="/api/v1/admin/analytics",
    tags=["Admin Analytics"],
)


@router.get("")
def admin_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return get_admin_analytics(db)


@router.get("/users/export")
def export_users_csv(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "email",
            "username",
            "display_name",
            "role",
            "is_verified",
            "is_active",
            "auth_provider",
            "created_at",
        ]
    )

    for user in users:
        writer.writerow(
            [
                str(user.id),
                user.email,
                user.username,
                user.display_name,
                user.role,
                user.is_verified,
                user.is_active,
                user.auth_provider,
                user.created_at,
            ]
        )

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                'attachment; filename="users.csv"'
            )
        },
    )