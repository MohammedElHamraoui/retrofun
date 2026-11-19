from sqlalchemy import func, intersect, select

from retrofun.db import SessionLocal
from retrofun.models import Country, Manufacturer, Product
from retrofun.models.customer import Customer
from retrofun.models.order import Order
from retrofun.models.order_item import OrderItem

if __name__ == "__main__":
    print("*** One-To-Many ***")

    # ONE single session for all queries
    with SessionLocal() as session:
        print("1. The list of products made by IBM and Texas Instruments.")
        q_ibm_ti = (
            select(Product)
            .join(Manufacturer)
            .where(Manufacturer.name.in_(["IBM", "Texas Instruments"]))
        )
        for product in session.scalars(q_ibm_ti):
            print(product)
        print("")

        print("2. Manufacturers that operate in Brazil.")
        q_brazil = (
            select(Manufacturer)
            .join(Product)
            .join(Product.countries)
            .where(Country.name == "Brazil")
            .distinct()
        )
        for maker in session.scalars(q_brazil):
            print(maker)
        print("")

        print('3. Products that have a manufacturer that has the word "Research" in their name.')
        q_research = select(Product).join(Manufacturer).where(Manufacturer.name.like("%Research%"))
        for product in session.scalars(q_research):
            print(product)
        print("")

        print("4. Manufacturers that made products based on the Z80 CPU or any of its clones.")
        q_z80 = select(Manufacturer).join(Product).where(Product.cpu.like("%Z80%")).distinct()
        for manufacturer in session.scalars(q_z80):
            print(manufacturer)
        print("")

        print(
            "5. Manufacturers that made products that are not based on the 6502 CPU "
            "or any of its clones."
        )
        q_6502 = (
            select(Manufacturer)
            .join(Product)
            .where(Product.cpu.not_like("%6502%"))
            .distinct()  # <-- Fixed: prevents duplicate manufacturers from the join
        )
        for manufacturer in session.scalars(q_6502):
            print(manufacturer)
        print("")

        print(
            "6. Manufacturers and the year they went to market with their first product, "
            "sorted by the year."
        )
        year_first = func.min(Product.year).label("year_first")
        q_first_year = (
            select(Manufacturer.name, year_first)
            .join(Product)
            .group_by(Manufacturer.id)  # <-- Fixed: group by PK, not name
            .order_by(year_first)
        )
        for row in session.execute(q_first_year):
            print(row)
        print("")

        print("7. Manufacturers that have 3 to 5 products in the catalog.")
        q_makers = (
            select(Manufacturer.name)
            .join(Product)
            .group_by(Manufacturer.id)
            .having(func.count(Product.id).between(3, 5))
        )
        for maker_name in session.scalars(q_makers):
            print(maker_name)
        print("")

        print("8. Manufacturers that operated for more than 5 years.")
        q_five = (
            select(Manufacturer)
            .join(Product)
            .group_by(Manufacturer.id)
            .having(func.max(Product.year) >= func.min(Product.year) + 5)
        )
        for manufacturer in session.scalars(q_five):
            print(manufacturer)
        print("")

        print("*** Many-To-Many ***")

        print("11. Products that were made in UK or USA.")
        q_uk_usa = (
            select(Product)
            .join(Product.countries)
            .where(Country.name.in_(["UK", "USA"]))
            .distinct()  # <-- Fixed: prevents duplicate products from the join
        )
        for product in session.scalars(q_uk_usa):
            print(product)
        print("")

        print(
            "12. Products not made in UK or USA. Products made in UK/USA jointly with other "
            "countries should be included."
        )
        q_uk_usa_other = (
            select(Product)
            .join(Product.countries)
            .where(Country.name.notin_(["UK", "USA"]))
            .distinct()
        )
        # <-- Fixed: was accidentally executing q_uk_usa again
        for product in session.scalars(q_uk_usa_other):
            print(product)
        print("")

        print("13. Countries with products based on the Z80 CPU or any of its clones.")
        stmt_z80 = (
            select(Country)
            .join(Country.products)
            .where(Product.cpu.like("%Z80%"))
            .distinct()
            .order_by(Country.name)
        )
        for country in session.scalars(stmt_z80):
            print(country)
        print("")

        print("14. Countries that had products made in the 1970s in alphabetical order.")
        q_1970 = (
            select(Country)
            .join(Country.products)
            .where(Product.year.between(1970, 1979))
            .distinct()
            .order_by(Country.name)
        )
        for country in session.scalars(q_1970):
            print(country)
        print("")

        print("15. The 5 countries with the most products. Ties broken alphabetically.")
        number_prod = func.count(Product.id).label("number_prod")
        q_cmp = (
            select(Country, number_prod)
            .join(Country.products)
            .group_by(Country.id)
            .order_by(number_prod.desc(), Country.name)
            .limit(5)
        )
        for r_cmp in session.execute(q_cmp):
            print(r_cmp)
        print("")

        print("16. Manufacturers that have more than 3 products in UK or USA.")
        q_m3_uk_usa = (
            select(Manufacturer)
            .join(Product)
            .join(Product.countries)
            .where(Country.name.in_(["UK", "USA"]))
            .group_by(Manufacturer.id)
            .having(func.count(Product.id.distinct()) > 3)  # <-- Fixed: count distinct products
        )
        for manufacturer in session.scalars(q_m3_uk_usa):
            print(manufacturer)
        print("")

        print("17. Manufacturers that have products in more than one country.")
        number_countries = func.count(Country.id.distinct()).label("number_countries")
        q_mpc = (
            select(Manufacturer, number_countries)
            .join(Product)
            .join(Product.countries)
            .group_by(Manufacturer.id)
            .having(number_countries > 1)
        )
        for r_mpc in session.execute(q_mpc):
            print(r_mpc)
        print("")

        print("18. Products made jointly in UK and USA.")
        q_p_uk = select(Product.id).join(Product.countries).where(Country.name == "UK")
        q_p_usa = select(Product.id).join(Product.countries).where(Country.name == "USA")

        # Intersect returns Product IDs. We fetch the actual objects by ID.
        intersect_stmt = intersect(q_p_uk, q_p_usa)
        product_ids = session.scalars(intersect_stmt).all()

        for pid in product_ids:
            print(
                session.get(Product, pid)
            )  # <-- Fixed: get() expects an integer ID, not an object

        print("*** Many-To-Many Product--OrderItems--Order ***")

        c = session.scalar(select(Customer).where(Customer.name == "John Butler"))
        print(c)
        assert c is not None
        print(c.orders)
        orders = session.scalars(c.orders.select()).all()
        print(orders)
        print(session.scalar(select(func.count(Customer.id))))
        print(session.scalar(select(func.count(Order.id))))

        item_total = (OrderItem.unit_price * OrderItem.quantity).label("item_total")
        q = (
            select(item_total, Product)
            .join(Product.order_items)
            .order_by(item_total.desc())
            .limit(3)
        )
        print(session.execute(q).all())
