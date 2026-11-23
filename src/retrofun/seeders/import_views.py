# src/retrofun/seeders/import_views.py
import csv
from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from retrofun.models import BlogArticle, BlogSession, BlogUser, BlogView
from retrofun.seeders.base import get_data_dir, get_db_session, parse_timestamp


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "views.csv"

    with get_db_session() as session:
        # 1. Pre-load existing records for N+1 prevention and idempotency
        articles_by_title: dict[str, BlogArticle] = {
            a.title: a for a in session.scalars(select(BlogArticle)).all()
        }
        sessions_by_id: dict[UUID, BlogSession] = {
            s.id: s for s in session.scalars(select(BlogSession)).all()
        }
        users_by_id: dict[UUID, BlogUser] = {
            u.id: u for u in session.scalars(select(BlogUser)).all()
        }

        # ✅ FIX: Use exact types (int, UUID, datetime) instead of "..."
        existing_views: set[tuple[int, UUID, datetime]] = {
            (v.article_id, v.session_id, v.created_at)
            for v in session.scalars(select(BlogView)).all()
        }

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            i = 0

            for row_num, row in enumerate(reader, start=2):
                # 2. Find or create BlogUser
                user_id_str = row.get("user", "").strip()
                if not user_id_str:
                    print(f"⚠️ Row {row_num}: Missing 'user' ID. Skipping.")
                    continue

                try:
                    user_id = UUID(user_id_str)
                except ValueError:
                    print(f"⚠️ Row {row_num}: Invalid user UUID '{user_id_str}'. Skipping.")
                    continue

                user = users_by_id.get(user_id)
                if user is None:
                    user = BlogUser(id=user_id)
                    session.add(user)
                    session.flush()  # Ensure ID is available for the session
                    users_by_id[user_id] = user

                # 3. Find or create BlogSession
                session_id_str = row.get("session", "").strip()
                if not session_id_str:
                    print(f"⚠️ Row {row_num}: Missing 'session' ID. Skipping.")
                    continue

                try:
                    session_id = UUID(session_id_str)
                except ValueError:
                    print(f"⚠️ Row {row_num}: Invalid session UUID '{session_id_str}'. Skipping.")
                    continue

                blog_session = sessions_by_id.get(session_id)
                if blog_session is None:
                    blog_session = BlogSession(id=session_id, user_id=user.id)
                    session.add(blog_session)
                    session.flush()
                    sessions_by_id[session_id] = blog_session

                # 4. Article MUST already exist (import_articles runs before this)
                title = row.get("title", "").strip()
                article: BlogArticle | None = articles_by_title.get(title)
                if article is None:
                    print(f"⚠️ Row {row_num}: Article '{title}' not found. Skipping.")
                    continue

                # 5. Parse timestamp
                try:
                    ts = parse_timestamp(row["timestamp"])
                except (ValueError, KeyError):
                    print(f"⚠️ Row {row_num}: Invalid timestamp. Skipping.")
                    continue

                # 6. Idempotency check on the composite business key
                view_key = (article.id, blog_session.id, ts)
                if view_key in existing_views:
                    continue
                existing_views.add(view_key)

                session.add(
                    BlogView(
                        article_id=article.id,
                        session_id=blog_session.id,
                        created_at=ts,
                    )
                )
                i += 1

                if i % 100 == 0:
                    print(f"  ...{i} views inserted")

        print(f"✅ Done: {i} new views inserted.")


if __name__ == "__main__":
    main()
