import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Automatically initialize and seed database on startup
    from seed import seed_database
    try:
        print("Running database initialization and seeding...")
        seed_database()
    except Exception as e:
        print(f"Error during auto-seeding: {e}")

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
