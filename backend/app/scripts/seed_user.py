from __future__ import annotations

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import User


def main() -> None:
    with SessionLocal() as db:
        existing = db.execute(
            select(User).where(User.display_name == "Dev User"),
        ).scalar_one_or_none()

        if existing is not None:
            print(f"User already exists: {existing.id}")
            return

        user = User(
            display_name="Dev User",
            role="user",
            locale="ru",
            timezone="Asia/Seoul",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    print(f"User created: {user.id}")


if __name__ == "__main__":
    main()
