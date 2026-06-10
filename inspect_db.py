from app import create_app
from models import db
from sqlalchemy import inspect, text


def main():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if not tables:
            print("No tables found.")
            return
        print("Tables found:")
        for t in tables:
            print(f"- {t}")
        for t in tables:
            print(f"\n=== {t} ===")
            cols = inspector.get_columns(t)
            for c in cols:
                print(f"{c['name']}: {c.get('type')}")
            try:
                count = db.session.execute(text(f"SELECT COUNT(*) FROM {t}"))
                print(f"rows: {list(count)[0][0]}")
            except Exception as e:
                print(f"rows: ? (error: {e})")


if __name__ == "__main__":
    main()
