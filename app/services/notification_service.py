from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id,
    notification_type: str,
    title: str,
    message: str,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        is_read=False,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_user_notifications(
    db: Session,
    user_id,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
):
    query = select(Notification).where(
        Notification.user_id == user_id
    )

    if unread_only:
        query = query.where(
            Notification.is_read.is_(False)
        )

    query = query.order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(limit)

    return db.scalars(query).all()


def get_unread_count(
    db: Session,
    user_id,
) -> int:
    count = db.scalar(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    )

    return count or 0


def mark_notification_read(
    db: Session,
    user_id,
    notification_id,
) -> Notification | None:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )

    if notification is None:
        return None

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_read(
    db: Session,
    user_id,
) -> int:
    notifications = db.scalars(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.commit()

    return len(notifications)