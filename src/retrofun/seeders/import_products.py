# src/retrofun/seeders/import_products.py
import csv
from typing import Any

from sqlalchemy import inspect, select

from retrofun.models import Country, Manufacturer, Product
from retrofun.seeders.base import get_data_dir, get_db_session


def main() -> None:
    data_dir = get_data_dir()
    csv_path = data_dir / "products.csv"

    with get_db_session() as session:
        # 1. Pre-load ALL existing records to ensure idempotency and avoid UniqueViolation
        manufacturers_by_name = {m.name: m for m in session.scalars(select(Manufacturer)).all()}
        countries_by_name = {c.name: c for c in session.scalars(select(Country)).all()}
        products_by_name = {p.name: p for p in session.scalars(select(Product)).all()}

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):
                # 2. Extract and clean fields
                fields: dict[str, Any] = {k: (v or None) for k, v in row.items() if v is not None}

                try:
                    fields["year"] = int(row["year"])
                except (ValueError, KeyError):
                    print(f"⚠️ Warning: Row {row_num} has invalid or missing year. Skipping.")
                    continue

                manufacturer_name_raw = fields.pop("manufacturer", "")
                if not isinstance(manufacturer_name_raw, str) or not manufacturer_name_raw.strip():
                    print(f"⚠️ Warning: Row {row_num} has missing manufacturer. Skipping.")
                    continue
                manufacturer_name = manufacturer_name_raw.strip()

                # Safely handle country field (can be empty or multiple separated by '/')
                country_field = fields.pop("country", "") or ""
                country_names = [c.strip() for c in str(country_field).split("/") if c.strip()]

                # Drop any extra CSV columns that aren't in the Product model
                valid_cols = {c.key for c in inspect(Product).mapper.column_attrs}
                fields = {k: v for k, v in fields.items() if k in valid_cols}

                # ✅ Explicitly validate product_name to satisfy mypy
                product_name_raw = fields.get("name")
                if not isinstance(product_name_raw, str) or not product_name_raw.strip():
                    print(
                        f"⚠️ Warning: Row {row_num} has missing or invalid product name. Skipping."
                    )
                    continue
                product_name = product_name_raw.strip()

                # 3. Find or Create Manufacturer
                if manufacturer_name not in manufacturers_by_name:
                    new_mfr = Manufacturer(name=manufacturer_name)
                    session.add(new_mfr)
                    manufacturers_by_name[manufacturer_name] = new_mfr
                manufacturer = manufacturers_by_name[manufacturer_name]

                # 4. Find or Create Countries
                product_countries = []
                for c_name in country_names:
                    if c_name not in countries_by_name:
                        new_country = Country(name=c_name)
                        session.add(new_country)
                        countries_by_name[c_name] = new_country
                    product_countries.append(countries_by_name[c_name])

                # 5. Find or Create Product
                if product_name in products_by_name:
                    # Product already exists, skip to maintain idempotency
                    continue

                product = Product(**fields)
                product.manufacturer = manufacturer
                product.countries = product_countries

                session.add(product)
                # Add to dict in case the CSV somehow has duplicate rows
                products_by_name[product_name] = product


if __name__ == "__main__":
    main()
