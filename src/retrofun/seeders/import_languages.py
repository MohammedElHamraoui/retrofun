# src/retrofun/seeders/import_languages.py
import csv

from sqlalchemy import select

from retrofun.models import BlogArticle, Language
from retrofun.seeders.base import get_data_dir, get_db_session


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "articles.csv"

    with get_db_session() as session:
        # 1. Pre-load existing records to avoid N+1 queries and ensure idempotency
        articles_by_title: dict[str, BlogArticle] = {
            a.title: a for a in session.scalars(select(BlogArticle))
        }
        languages_by_name: dict[str, Language] = {
            lg.name: lg for lg in session.scalars(select(Language))
        }

        # 2. Process the CSV
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                article_title = row.get("title", "").strip()
                article = articles_by_title.get(article_title)

                if not article:
                    print(
                        f"⚠️ Warning: Row {row_num} - Article '{article_title}' not found. Skipping."
                    )
                    continue

                # 3. Handle Language (Find or Create)
                language_name = row.get("language", "").strip()
                if language_name:
                    language = languages_by_name.get(language_name)
                    if language is None:
                        # ✅ No redundant DB query needed. Pre-load guarantees it's truly new.
                        language = Language(name=language_name)
                        session.add(language)
                        languages_by_name[language_name] = language

                    article.language = language

                # 4. Handle Translation (Find Only)
                translation_title = row.get("translation_of", "").strip()
                if translation_title:
                    translation_of = articles_by_title.get(translation_title)
                    if translation_of is None:
                        print(
                            f"⚠️ Warning: Row {row_num} - Translation target "
                            f"'{translation_title}' not found. Skipping translation link."
                        )
                    else:
                        article.translation_of = translation_of

                # ✅ SQLAlchemy's unit of work will only issue an UPDATE if the
                # foreign keys actually changed, making this perfectly idempotent.
                session.add(article)

        print("✅ Language and translation mappings updated successfully.")


if __name__ == "__main__":
    main()
