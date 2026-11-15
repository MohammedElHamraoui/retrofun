import csv
from pathlib import Path
from typing import Any

from retrofun.db import Base, SessionLocal, engine
from retrofun.models import Product


def main() -> None:
    data_dir = Path(__file__).parents[2] / "raw_data"
    # print(data_dir)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session, session.begin(), open(data_dir / "products.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fields: dict[str, Any] = {k: (v or None) for k, v in row.items()}
            fields["year"] = int(row["year"])
            product = Product(**fields)
            session.add(product)


if __name__ == "__main__":
    main()
