import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'users' AND table_schema = 'public';
    """))
    print("Columns in public.users table:")
    for row in result:
        print(row)

    result2 = conn.execute(text("""
        SELECT tc.constraint_name, tc.constraint_type
        FROM information_schema.table_constraints tc
        WHERE tc.table_name = 'users' AND tc.table_schema = 'public';
    """))
    print("\nConstraints on public.users table:")
    for row in result2:
        print(row)