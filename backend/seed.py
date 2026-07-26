from app.core.database import SessionLocal, db
from app.models.user import Department, User


def seed_database():
    print("Recreating database tables...")
    db.create_all()

    session = SessionLocal()
    try:
        print("Seeding departments...")
        depts_data = [
            ("Legal", "Legal review and compliance checking"),
            ("Compliance", "Global compliance and security auditing"),
            ("Procurement", "Vendor contract management and purchasing"),
            ("Engineering", "Technical policies and security controls"),
            ("HR", "Human resources policies and guidelines"),
        ]

        dept_map = {}
        for name, desc in depts_data:
            dept = session.query(Department).filter(Department.name == name).first()
            if not dept:
                dept = Department(name=name, description=desc)
                session.add(dept)
                session.flush()
            dept_map[name] = dept

        print("Seeding users...")
        users_data = [
            ("admin@company.com", "admin123", "System Admin", "Admin", "Compliance"),
            (
                "officer@company.com",
                "officer123",
                "Compliance Officer",
                "Compliance Officer",
                "Compliance",
            ),
            (
                "legal@company.com",
                "legal123",
                "Legal Reviewer",
                "Legal Reviewer",
                "Legal",
            ),
            (
                "auditor@company.com",
                "auditor123",
                "Internal Auditor",
                "Auditor",
                "Procurement",
            ),
            (
                "viewer@company.com",
                "viewer123",
                "Standard Viewer",
                "Viewer",
                "Engineering",
            ),
        ]

        for email, pwd, name, role, dept_name in users_data:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    full_name=name,
                    role=role,
                    department_id=dept_map[dept_name].id,
                    is_verified=True,
                    is_active=True,
                )
                user.set_password(pwd)
                session.add(user)
                print(f"Created user: {email} with role {role}")
            else:
                print(f"User: {email} already exists")

        session.commit()
        print("Seeding complete.")
    except Exception as e:
        session.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
