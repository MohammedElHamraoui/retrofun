import csv
from pathlib import Path
from typing import Any

from sqlalchemy import inspect

from retrofun.db import SessionLocal
from retrofun.models import Country, Manufacturer, Product


def main() -> None:
    data_dir = Path(__file__).parents[2] / "raw_data"

    with SessionLocal() as session, session.begin(), open(data_dir / "products.csv") as f:
        reader = csv.DictReader(f)
        all_manufacturers: dict[str, Manufacturer] = {}
        all_countries: dict[str, Country] = {}

        for row in reader:
            fields: dict[str, Any] = {k: (v or None) for k, v in row.items()}
            fields["year"] = int(row["year"])
            manufacturer = fields.pop("manufacturer")

            # Safely handle empty country fields
            country_field = fields.pop("country", "") or ""
            countries = [c.strip() for c in country_field.split("/") if c.strip()]

            # Drop any extra CSV columns that aren't in the Product model
            valid_cols = {c.key for c in inspect(Product).mapper.column_attrs}
            fields = {k: v for k, v in fields.items() if k in valid_cols}

            product = Product(**fields)

            if manufacturer not in all_manufacturers:
                m = Manufacturer(name=manufacturer)
                session.add(m)
                all_manufacturers[manufacturer] = m
            all_manufacturers[manufacturer].products.append(product)

            for country in countries:
                if country not in all_countries:
                    c = Country(name=country)
                    session.add(c)
                    all_countries[country] = c
                all_countries[country].products.append(product)


if __name__ == "__main__":
    main()
