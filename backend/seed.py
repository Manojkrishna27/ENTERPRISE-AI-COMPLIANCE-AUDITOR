from app import create_app
from app.database import db
from app.models.user import Department, User
from app.models.policy import Policy
import uuid

def seed_database():
    app = create_app()
    with app.app_context():
        print("Recreating database tables...")
        db.create_all()

        print("Seeding departments...")
        depts_data = [
            ("Legal", "Legal review and compliance checking"),
            ("Compliance", "Global compliance and security auditing"),
            ("Procurement", "Vendor contract management and purchasing"),
            ("Engineering", "Technical policies and security controls"),
            ("HR", "Human resources policies and guidelines")
        ]
        
        dept_map = {}
        for name, desc in depts_data:
            dept = Department.query.filter_by(name=name).first()
            if not dept:
                dept = Department(name=name, description=desc)
                db.session.add(dept)
                db.session.flush() # Populate ID
            dept_map[name] = dept

        print("Seeding users...")
        users_data = [
            ("admin@company.com", "admin123", "System Admin", "Admin", "Compliance"),
            ("officer@company.com", "officer123", "Compliance Officer", "Compliance Officer", "Compliance"),
            ("legal@company.com", "legal123", "Legal Reviewer", "Legal Reviewer", "Legal"),
            ("auditor@company.com", "auditor123", "Internal Auditor", "Auditor", "Procurement"),
            ("viewer@company.com", "viewer123", "Standard Viewer", "Viewer", "Engineering"),
        ]

        for email, pwd, name, role, dept_name in users_data:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    full_name=name,
                    role=role,
                    department_id=dept_map[dept_name].id,
                    is_verified=True,
                    is_active=True
                )
                user.set_password(pwd)
                db.session.add(user)
                print(f"Created user: {email} with role {role}")
            else:
                print(f"User: {email} already exists")

        db.session.commit()
        print("Seeding complete.")

if __name__ == '__main__':
    seed_database()
