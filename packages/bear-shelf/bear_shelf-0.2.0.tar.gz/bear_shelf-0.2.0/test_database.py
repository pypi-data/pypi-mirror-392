from argparse import ArgumentParser, Namespace
from html import parser
import timeit

from sqlalchemy.orm import DeclarativeMeta, Mapped, mapped_column

from bear_shelf.database import BearShelfDB, DatabaseConfig, bearshelf_default_db
from funcy_bear.randoms import rchoice

Base: DeclarativeMeta = BearShelfDB.get_base()


class TestModel(Base):
    __tablename__ = "test_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    email: Mapped[str] = mapped_column()


random_names = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
    "Mallory",
    "Niaj",
    "Olivia",
    "Peggy",
    "Rupert",
    "Sybil",
    "Trent",
    "Uma",
    "Victor",
    "Wendy",
    "Xander",
    "Yvonne",
    "Zack",
]


def generate_users(n: int) -> list[TestModel]:
    users: list[TestModel] = []
    for _ in range(n):
        name: str = rchoice(random_names)
        age: int = rchoice(range(18, 65))
        rnd_id: int = rchoice(range(1000, 9999))
        email: str = f"{name.lower()}_{rnd_id}@example.com"
        user = TestModel(name=name, age=age, email=email)
        users.append(user)
    return users


def database_operations_test(n: int = 10) -> None:
    config: DatabaseConfig = bearshelf_default_db(path="database.toml")
    new_users: list[TestModel] = []
    new_users.extend(generate_users(n))
    with BearShelfDB(database_config=config, enable_wal=True, records={"test_model": TestModel}) as db:
        db.create_tables()
        with db.open_session() as session:
            session.add_all(new_users)


if __name__ == "__main__":
    parser = ArgumentParser(description="Test Database Operations")
    parser.add_argument(
        "-n",
        "--num-records",
        type=int,
        default=1000,
        help="Number of test records to insert into the database",
    )
    args: Namespace = parser.parse_args()
    RUNS = args.num_records
    time: float = timeit.timeit(lambda: database_operations_test(n=RUNS), number=1)
    average: float = (time / RUNS) * 1000  # ms
    print(f"Inserted {RUNS} records in {time:.4f} seconds (average {average:.6f} ms per record)")
