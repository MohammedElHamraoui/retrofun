# src/retrofun/seeders/import_views.py
import csv
from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from retrofun.models import BlogArticle, BlogSession, BlogView
from retrofun.seeders.base import get_data_dir, get_db_session, parse_timestamp


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "views.csv"

    with get_db_session() as session:
        # 1. Pre-load for N+1 prevention and idempotency
        articles_by_title: dict[str, BlogArticle] = {
            a.title: a for a in session.scalars(select(BlogArticle)).all()
        }
        sessions_by_id: dict[UUID, BlogSession] = {
            s.id: s for s in session.scalars(select(BlogSession)).all()
        }

        # ✅ STRICTLY follows blog_view.py source of truth: v.created_at
        existing_views: set[tuple[int, UUID, datetime]] = {
            (v.article_id, v.session_id, v.created_at)
            for v in session.scalars(select(BlogView)).all()
        }

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            i = 0

            for row_num, row in enumerate(reader, start=2):
                title = row.get("article", "").strip()

                article: BlogArticle | None = articles_by_title.get(title)
                if article is None:
                    print(f"⚠️ Row {row_num}: Article '{title}' not found. Skipping.")
                    continue

                session_id = UUID(row["session_id"])

                blog_session: BlogSession | None = sessions_by_id.get(session_id)
                if blog_session is None:
                    print(f"⚠️ Row {row_num}: Session {session_id} not found. Skipping.")
                    continue

                try:
                    ts = parse_timestamp(row["timestamp"])
                except (ValueError, KeyError):
                    print(f"⚠️ Row {row_num}: Invalid timestamp. Skipping.")
                    continue

                # Idempotency check
                view_key = (article.id, blog_session.id, ts)
                if view_key in existing_views:
                    continue
                existing_views.add(view_key)

                # ✅ STRICTLY follows blog_view.py source of truth: created_at=ts
                view = BlogView(
                    article_id=article.id,
                    session_id=blog_session.id,
                    created_at=ts,
                )
                session.add(view)
                i += 1

                if i % 100 == 0:
                    print(f"  ...{i} views inserted")

        print(f"✅ Done: {i} new views inserted.")


if __name__ == "__main__":
    main()
