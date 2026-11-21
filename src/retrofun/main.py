from datetime import date, datetime

from sqlalchemy import func, intersect, select, text

from retrofun.db import SessionLocal
from retrofun.models import Country, Manufacturer, Product
from retrofun.models.customer import Customer
from retrofun.models.order import Order
from retrofun.models.order_item import OrderItem
from retrofun.models.product_review import ProductReview

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

        # ✅ Fix: Single query instead of N+1 session.get() calls
        products = session.scalars(select(Product).where(Product.id.in_(product_ids))).all()
        for p in products:
            print(p)
        print("")

        print("*** Many-To-Many Product--OrderItems--Order ***")

        print(
            "21. Orders above $300 in descending ordered by the sale amount from highest to lowest."
        )
        orders_above_300 = session.scalars(
            select(Order).where(Order.total_amount > 300).order_by(Order.total_amount.desc())
        )
        for order_above_300 in orders_above_300:
            print(order_above_300)
        print("")

        print("22. Orders that include one or more ZX81 computers.")
        orders_zx81 = session.scalars(
            select(Order)
            .join(Order.order_items)
            .join(OrderItem.product)
            .where(Product.name.like("%ZX81%"))
        )
        for order_zx81 in orders_zx81:
            print(order_zx81)
        print("")

        print("23. Orders that include a product made by Amstrad.")
        orders_amstrad = session.scalars(
            select(Order)
            .join(Order.order_items)
            .join(OrderItem.product)
            .join(Product.manufacturer)
            .where(Manufacturer.name == "Amstrad")
            .distinct()
        )
        for order_amstrad in orders_amstrad:
            print(order_amstrad)
        print("")

        print("24. Orders made on the 25th of December 2022 with two or more line items.")
        orders_new_eve = session.scalars(
            select(Order)
            .join(Order.order_items)
            .where(func.date(Order.created_at) == date(2022, 12, 25))
            .group_by(Order.id)
            .having(func.count(OrderItem.order_id) > 1)
        )
        for order_new_eve in orders_new_eve:
            print(order_new_eve)
        print("")

        print(
            "25. Customers with their first and last order date and time. "
            "Hint: the min() and max() functions can help with this query."
        )
        customers_min_max = session.execute(
            select(Customer, func.min(Order.created_at), func.max(Order.created_at))
            .join(Customer.orders)
            .group_by(Customer.id)
        )
        for customer_min_max in customers_min_max:
            print(customer_min_max)
        print("")

        print(
            "26. The top 5 manufacturers that had the most sale amounts, "
            "sorted by those amounts in descending order."
        )
        most_sale_makers = session.execute(
            select(
                Manufacturer.name,
                func.sum(OrderItem.unit_price * OrderItem.quantity).label("total_sales"),
            )
            .join(Manufacturer.products)
            .join(Product.order_items)
            .join(OrderItem.order)
            .group_by(Manufacturer.id)
            .order_by(text("total_sales DESC"))
            .limit(5)
        )
        for most_sale_maker in most_sale_makers:
            print(most_sale_maker)
        print("")

        print(
            "27. Products, their average star rating and their review count, "
            "sorted by review count in descending order"
        )
        product_rating = func.avg(ProductReview.rating).label("product_rating")
        products_rating_review = session.execute(
            select(Product, product_rating, func.count(ProductReview.rating))
            .join(Product.reviews)
            .group_by(Product.id)
            .order_by(product_rating)
        )
        for product_rating_review in products_rating_review:
            print(product_rating_review)
        print("")

        print(
            "28. Products and their average star rating, but only counting reviews "
            "that include a written comment."
        )
        q28 = (
            select(Product, func.avg(ProductReview.rating).label("product_rating"))
            .join(Product.reviews)
            .where(ProductReview.comment.is_not(None))
            .group_by(Product.id)
        )
        for r_28 in session.execute(q28):
            print(r_28)
        print("")

        print("29. Average star rating for the Commodore 64 computer in each month of 2022.")
        month_sell = func.extract("month", ProductReview.created_at).label("month_sell")
        q_29 = (
            select(Product, func.avg(ProductReview.rating), month_sell)
            .join(Product.reviews)
            .where(
                Product.name.ilike("%Commodore 64%"),
                ProductReview.created_at.between(datetime(2022, 1, 1), datetime(2022, 12, 31)),
            )
            .group_by(Product.id, month_sell)
            .order_by(month_sell)
        )
        for r_29 in session.execute(q_29):
            print(r_29)
        print("")

        print(
            "30. Customers with the minimum and maximum star rating they gave to a product, "
            "sorted alphabetically by customer name."
        )
        q_30 = (
            select(
                Customer,
                Product,
                func.min(ProductReview.rating).label("min_rating"),
                func.max(ProductReview.rating).label("max_rating"),
            )
            .join(Customer.product_reviews)
            .join(ProductReview.product)
            .group_by(Customer.id, Product.id)
            .order_by(Customer.name)
        )
        for r_30 in session.execute(q_30):
            print(r_30)
        print("")

        print(
            "31. Manufacturers with their average star rating, "
            "sorted from highest to lowest rating."
        )
        avg_rating = func.avg(ProductReview.rating).label("avg_rating")
        q_31 = (
            select(Manufacturer, avg_rating)
            .join(Manufacturer.products)
            .join(Product.reviews)
            .group_by(Manufacturer.id)
            .order_by(avg_rating.desc())
        )
        for r_31 in session.execute(q_31):
            print(r_31)
        print("")

        print(
            "32. Product countries with their average star rating, "
            "sorted from highest to lowest rating."
        )
        avg_rating = func.avg(ProductReview.rating).label("avg_rating")
        q_32 = (
            select(Country, avg_rating)
            .join(Country.products)
            .join(Product.reviews)
            .group_by(Country.id)
            .order_by(avg_rating.desc())
        )
        for r_32 in session.execute(q_32):
            print(r_32)
