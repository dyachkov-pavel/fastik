from envparse import Env

env = Env()

DATABASE_URL = env.str(
    "DATABASE_URL",
    default="postgresql+asyncpg://ppp:111@0.0.0.0:5432/fastapi",
)  # connect string for the real database

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://ppp_test:111_test@0.0.0.0:5433/fastapi_test",
)
