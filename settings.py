from envparse import Env

env = Env()

DATABASE_URL = env.str(
    "DATABASE_URL",
    default="postgresql+asyncpg://ppp:111@127.0.0.1:5432/fastapi",
)  # drivers://user:pass@host:port/db-name

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://ppp_test:111_test@127.0.0.1:5433/fastapi_test",
)
