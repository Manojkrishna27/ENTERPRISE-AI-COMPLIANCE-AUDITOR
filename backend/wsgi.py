import os

import uvicorn

if __name__ == "__main__":
    from seed import seed_database

    try:
        print("Running database initialization and seeding...")
        seed_database()
    except Exception as e:
        print(f"Error during auto-seeding: {e}")

    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
