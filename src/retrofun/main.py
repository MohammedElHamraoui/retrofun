from sqlalchemy import func, select

from retrofun.db import SessionLocal
from retrofun.models import Product
from retrofun.models.manufacturer import Manufacturer

if __name__ == "__main__":
    with SessionLocal() as session, session.begin():
        print("1. The list of products made by IBM and Texas Instruments.")
        with SessionLocal() as session, session.begin():
            q_ibm_ti = (
                select(Product)
                .join(Manufacturer)
                .where(Manufacturer.name.in_(["IBM", "Texas Instruments"]))
            )
            r_ibm_ti = session.scalars(q_ibm_ti)
            for product in r_ibm_ti:
                print(product)
    print("")

    print("2. Manufacturers that operate in Brazil.")
    with SessionLocal() as session, session.begin():
        q_brazil = select(Manufacturer).join(Product).where(Product.country == "Brazil")
        r_brazil = session.scalars(q_brazil)
        for maker in r_brazil:
            print(maker)
    print("")

    print('3. Products that have a manufacturer that has the word "Research" in their name.')
    with SessionLocal() as session, session.begin():
        q_research = select(Product).join(Manufacturer).where(Manufacturer.name.like("%Research%"))
        r_research = session.scalars(q_research)
        for product in r_research:
            print(product)
    print("")

    print("4. Manufacturers that made products based on the Z80 CPU or any of its clones.")
    with SessionLocal() as session, session.begin():
        q_z80 = select(Manufacturer).join(Product).where(Product.cpu.like("%Z80%")).distinct()
        r_z80 = session.scalars(q_z80)
        for manufacturer in r_z80:
            print(manufacturer)
    print("")

    print(
        "5. Manufacturers that made products that are not based on the 6502 CPU "
        "or any of its clones."
    )
    with SessionLocal() as session, session.begin():
        q_6502 = select(Manufacturer).join(Product).where(Product.cpu.not_like("%6502%")).distinct()
        r_6502 = session.scalars(q_6502)
        for manufacturer in r_6502:
            print(manufacturer)
    print("")

    print(
        "6. Manufacturers and the year they went to market with their first product, "
        "sorted by the year."
    )
    with SessionLocal() as session, session.begin():
        year_first = func.min(Product.year).label("year_first")
        query = (
            select(Manufacturer.name, year_first)
            .join(Product)
            .group_by(Manufacturer.name)
            .order_by(year_first)
        )
        results = session.execute(query)
        for row in results:
            print(row)
    print("")

    print("7. Manufacturers that have 3 to 5 products in the catalog.")
    with SessionLocal() as session, session.begin():
        q_makers = (
            select(Manufacturer.name)
            .join(Product)
            .group_by(Manufacturer.id)
            .having(func.count(Product.id).between(3, 5))
        )
        results_makers = session.scalars(q_makers)
        for result_marker in results_makers:
            print(result_marker)
    print("")

    print("8. Manufacturers that operated for more than 5 years.")
    with SessionLocal() as session, session.begin():
        q_five = (
            select(Manufacturer)
            .join(Product)
            .group_by(Manufacturer.id)
            .having(func.max(Product.year) >= func.min(Product.year) + 5)
        )
        results_five = session.scalars(q_five)
        for result_five in results_five:
            print(result_five)
