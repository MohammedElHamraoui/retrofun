# src/retrofun/import_articles.py
import csv

from sqlalchemy import select

from retrofun.models import BlogArticle, BlogAuthor, Product
from retrofun.seeders.base import get_data_dir, get_db_session, parse_timestamp


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "articles.csv"

    with get_db_session() as session:
        # 1. Pre-load Authors and Products into memory to avoid N+1 queries
        authors_by_name = {a.name: a for a in session.scalars(select(BlogAuthor)).all()}
        products_by_name = {p.name: p for p in session.scalars(select(Product)).all()}

        # 2. Process the CSV
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(
                reader, start=2
            ):  # start=2 accounts for 1-based index + header
                author_name = row.get("author", "").strip()
                author = authors_by_name.get(author_name)

                if not author:
                    print(f"⚠️ Warning: Row {row_num} - Author '{author_name}' not found. Skipping.")
                    continue

                # ✅ Clean timestamp parsing
                created_at = parse_timestamp(row["timestamp"])

                # Handle optional product (product_id is nullable in BlogArticle)
                product_name = row.get("product", "").strip()
                product = products_by_name.get(product_name) if product_name else None

                if product_name and not product:
                    print(
                        f"⚠️ Warning: Row {row_num} - Product '{product_name}' not found "
                        "in database. Skipping."
                    )
                    continue

                # 3. Create and add the BlogArticle
                article = BlogArticle(
                    title=row["title"].strip(),
                    author_id=author.id,
                    product_id=product.id if product else None,
                    created_at=created_at,
                )
                session.add(article)


if __name__ == "__main__":
    main()
