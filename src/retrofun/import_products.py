import csv
from pathlib import Path

from retrofun.database import Base, Product, SessionLocal, engine


def main() -> None:
    data_dir = Path(__file__).parents[2] / "raw_data"
    # print(data_dir)

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session, session.begin(), open(data_dir / "products.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["year"] = int(row["year"])
            product = Product(**row)
            # print(product)
            session.add(product)


if __name__ == "__main__":
    main()
