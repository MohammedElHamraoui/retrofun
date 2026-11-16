import csv
from pathlib import Path
from typing import Any

from retrofun.db import Base, SessionLocal, engine
from retrofun.models import Manufacturer, Product


def main() -> None:
    data_dir = Path(__file__).parents[2] / "raw_data"
    # print(data_dir)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session, session.begin(), open(data_dir / "products.csv") as f:
        reader = csv.DictReader(f)
        all_manufacturers = {}

        for row in reader:
            fields: dict[str, Any] = {k: (v or None) for k, v in row.items()}
            fields["year"] = int(row["year"])

            manufacturer = fields.pop("manufacturer")
            product = Product(**fields)

            if manufacturer not in all_manufacturers:
                m = Manufacturer(name=manufacturer)
                session.add(m)
                all_manufacturers[manufacturer] = m
            all_manufacturers[manufacturer].products.append(product)


if __name__ == "__main__":
    main()
