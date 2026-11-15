from sqlalchemy import func, or_, select

from retrofun.db import SessionLocal
from retrofun.models import Product

if __name__ == "__main__":
    print("1. The first three products in alphabetical order built in the year 1983.")
    with SessionLocal() as session, session.begin():
        q_products = select(Product).where(Product.year == 1983).order_by(Product.name).limit(3)
        r = session.scalars(q_products).all()
        for product in r:
            print(product.to_dict())
    print("")

    print(
        "2. Products that use the 'Z80' CPU or any of its clones. Assume that all products"
        " based on this CPU have the word 'Z80' in the cpu column."
    )
    with SessionLocal() as session, session.begin():
        q_products = select(Product).where(Product.cpu.like("%Z80%"))
        r = session.scalars(q_products).all()
        for product in r:
            print(product.to_dict())
    print("")

    print(
        '3. Products that use either the "Z80" or the "6502" CPUs, or any of its clones, '
        "built before 1990, sorted alphabetically by name."
    )
    with SessionLocal() as session, session.begin():
        q_products = (
            select(Product)
            .where(or_(Product.cpu.like("%Z80%"), Product.cpu.like("%6502%")), Product.year < 1990)
            .order_by(Product.name)
        )
        r = session.scalars(q_products).all()
        for product in r:
            print(product.to_dict())
    print("")

    print("4. The manufacturers that built products in the 1980s.")
    with SessionLocal() as session, session.begin():
        q_makers = select(Product.manufacturer).where(Product.year.between(1980, 1989)).distinct()
        r_4 = session.scalars(q_makers).all()
        for manufacturer in r_4:
            print(manufacturer)
    print("")

    print('5. Manufacturers whose names start with the letter "T", sorted alphabetically.')
    with SessionLocal() as session, session.begin():
        q_makers = (
            select(Product.manufacturer)
            .where(Product.manufacturer.like("T%"))
            .distinct()
            .order_by(Product.manufacturer)
        )
        r_5 = session.scalars(q_makers).all()
        for manufacturer in r_5:
            print(manufacturer)
    print("")

    print(
        "6. The first and last years in which products have been built in Croatia, "
        "along with the number of products built."
    )
    with SessionLocal() as session, session.begin():
        q = (
            select(func.min(Product.year), func.max(Product.year), func.count(Product.id))
            .group_by(Product.country)
            .having(Product.country == "Croatia")
        )
        rows = session.execute(q).all()
        for row in rows:
            print(row)
    print("")

    print(
        "7. The number of products that were built each year. The results should start from "
        "the year with the most products, to the year with the least. Years in which no products "
        "were built do not need to be included."
    )
    with SessionLocal() as session, session.begin():
        q_7 = (select(Product.year, func.count(Product.id)).group_by(Product.year)).order_by(
            func.count(Product.id).desc()
        )
        rows_7 = session.execute(q_7).all()
        for row_7 in rows_7:
            print(row_7)
    print("")

    print(
        "8. The number of manufacturers in the United States "
        "(note that the country field for these products is set to USA)"
    )
    with SessionLocal() as session, session.begin():
        q_8 = (
            select(func.count(Product.manufacturer.distinct())).group_by(Product.country)
        ).having(Product.country == "USA")
        row = session.scalar(q_8)
        print(row)
    print("")

    # c64 = Product(name="Commodore 64", manufacturer="Commodore")
    # print(f"c64: {c64}")
    # print(c64.to_dict())

    # with SessionLocal() as session, session.begin():
    #     q = select(Product).where(Product.manufacturer == "Commodore")
    #     r = session.scalars(q).all()
    #     for row in r:
    #         print(row)

    #     q = select(Product).where(Product.manufacturer == "Commodore")
    #     r = session.scalar(q)
    #     print(r)

    #     q = select(Product).where(Product.year >= 1990)
    #     r = session.scalars(q).all()
    #     for row in r:
    #         print(row)

    #     q = select(Product).where(Product.manufacturer == "Commodore", Product.year == 1980)
    #     r = session.scalars(q).all()
    #     for row in r:
    #         print(row)

    #     q = select(Product).where(or_(Product.year < 1970, Product.year > 1990))
    #     r = session.scalars(q).all()
    #     for row in r:
    #         print(row)

    #     q = select(Product).where(Product.name.like("%Sinclair%"))
    #     r = session.scalars(q).all()
    #     for row in r:
    #         print(row)

    #     qq = select(Product.name, Product.manufacturer).order_by(Product.name)
    #     rr = session.execute(qq).all()
    #     for product in rr:
    #         print(product)

    #     q = select(func.count(Product.id))
    #     r = session.scalar(q)
    #     print(f"count: {r}")
