from typing import Any

from sqlalchemy import func, or_, select

from retrofun.database import Product, SessionLocal


def model_to_dict(obj: Any) -> dict[str, str | int | None]:
    """Converts a SQLAlchemy ORM model instance into a dictionary."""
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


if __name__ == "__main__":
    c64 = Product(name="Commodore 64", manufacturer="Commodore")
    print(f"c64: {c64}")
    c64_dict = model_to_dict(c64)
    print(c64_dict)

    with SessionLocal() as session, session.begin():
        q = select(Product).where(Product.manufacturer == "Commodore")
        r = session.scalars(q).all()
        for row in r:
            print(row)

        q = select(Product).where(Product.manufacturer == "Commodore")
        r = session.scalar(q)
        print(r)

        q = select(Product).where(Product.year >= 1990)
        r = session.scalars(q).all()
        for row in r:
            print(row)

        q = select(Product).where(Product.manufacturer == "Commodore", Product.year == 1980)
        r = session.scalars(q).all()
        for row in r:
            print(row)

        q = select(Product).where(or_(Product.year < 1970, Product.year > 1990))
        r = session.scalars(q).all()
        for row in r:
            print(row)

        q = select(Product).where(Product.name.like("%Sinclair%"))
        r = session.scalars(q).all()
        for row in r:
            print(row)

        qq = select(Product.name, Product.manufacturer).order_by(Product.name)
        rr = session.execute(qq).all()
        for product in rr:
            print(product)

        q = select(func.count(Product.id))
        r = session.scalar(q)
        print(f"count: {r}")
