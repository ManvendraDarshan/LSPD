from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.enums import UserRole, VerificationStatus
from app.models.provider import ProviderService, ServiceCategory, ServiceProvider
from app.models.review import Review
from app.models.user import User
from app.services.provider_service import make_location

PASSWORD = "DemoPass@123"

CATEGORIES = [
    ("Electrician", "electrician"),
    ("Plumber", "plumber"),
    ("Carpenter", "carpenter"),
    ("Painter", "painter"),
    ("Mechanic", "mechanic"),
    ("Cleaner", "cleaner"),
    ("AC Repair", "ac-repair"),
    ("Appliance Repair", "appliance-repair"),
    ("Mobile Repair", "mobile-repair"),
    ("Computer Repair", "computer-repair"),
    ("RO Repair", "ro-repair"),
    ("Pest Control", "pest-control"),
    ("Salon/Beautician", "salon-beautician"),
    ("Tutor", "tutor"),
    ("Other", "other"),
]

PROVIDERS = [
    ("provider@example.com", "Ramesh Sharma", "Satna Reliable Electric Works", "Electrician", "Certified electrician for home wiring, inverter setup, switches, MCB panels and emergency fault repairs.", 12, "Satna", "Satna", 24.5854, 80.8272, True),
    ("plumber@example.com", "Amit Verma", "Amit Pipe Care", "Plumber", "Leak repair, bathroom fittings, water tank line setup and kitchen plumbing across Rewa and nearby colonies.", 9, "Rewa", "Rewa", 24.5362, 81.3037, True),
    ("ac@example.com", "Imran Khan", "Bhopal CoolCare AC Service", "AC Repair", "Split and window AC installation, gas refill, servicing and compressor troubleshooting with doorstep support.", 8, "Bhopal", "Bhopal", 23.2599, 77.4126, True),
    ("paint@example.com", "Neha Patel", "Indore Smart Paints", "Painter", "Interior and exterior painting, waterproof coating, texture walls and color consultation for homes and shops.", 7, "Indore", "Indore", 22.7196, 75.8577, False),
    ("carpenter@example.com", "Sanjay Sahu", "Jabalpur Woodcraft", "Carpenter", "Custom furniture repair, modular kitchen fittings, doors, wardrobes and polish work.", 15, "Jabalpur", "Jabalpur", 23.1815, 79.9864, True),
    ("mechanic@example.com", "Vikas Yadav", "Gwalior Quick Mechanics", "Mechanic", "Two-wheeler and car roadside assistance, general service, battery jumpstart and minor repairs.", 10, "Gwalior", "Gwalior", 26.2183, 78.1828, False),
]


def get_or_create_user(db, email, name, phone, role, city, district):
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(
        email=email,
        name=name,
        phone=phone,
        role=role,
        city=city,
        district=district,
        password_hash=hash_password(PASSWORD),
    )
    db.add(user)
    db.flush()
    return user


def main():
    db = SessionLocal()
    try:
        admin = get_or_create_user(db, "admin@example.com", "Demo Super Admin", "9000000001", UserRole.admin, "Bhopal", "Bhopal")
        customer = get_or_create_user(db, "customer@example.com", "Demo Customer", "9000000002", UserRole.customer, "Satna", "Satna")
        get_or_create_user(db, "customer2@example.com", "Anjali Tiwari", "9000000003", UserRole.customer, "Rewa", "Rewa")

        category_map = {}
        for name, slug in CATEGORIES:
            category = db.scalar(select(ServiceCategory).where(ServiceCategory.slug == slug))
            if not category:
                category = ServiceCategory(name=name, slug=slug, description=f"Trusted local {name.lower()} professionals")
                db.add(category)
                db.flush()
            category_map[name] = category

        for idx, (email, name, business, category_name, desc, exp, city, district, lat, lng, verified) in enumerate(PROVIDERS, start=10):
            user = get_or_create_user(db, email, name, f"90000000{idx}", UserRole.provider, city, district)
            provider = user.provider_profile
            if not provider:
                provider = ServiceProvider(
                    user_id=user.id,
                    business_name=business,
                    description=desc,
                    experience=exp,
                    address=f"Main Road, {city}, Madhya Pradesh",
                    city=city,
                    district=district,
                    state="Madhya Pradesh",
                    pincode="485001",
                    latitude=lat,
                    longitude=lng,
                    location=make_location(lng, lat),
                    working_hours="Mon-Sat, 9:00 AM - 7:00 PM",
                    verification_status=VerificationStatus.verified if verified else VerificationStatus.pending,
                    is_verified=verified,
                )
                db.add(provider)
                db.flush()
                db.add(ProviderService(provider_id=provider.id, category_id=category_map[category_name].id))

        db.flush()
        providers = db.scalars(select(ServiceProvider)).all()
        for provider in providers:
            exists = db.scalar(select(Review).where(Review.customer_id == customer.id, Review.provider_id == provider.id))
            if not exists:
                db.add(
                    Review(
                        customer_id=customer.id,
                        provider_id=provider.id,
                        rating=5 if provider.is_verified else 4,
                        comment=f"Demo review: reliable service from {provider.business_name}. Clear communication and timely work.",
                    )
                )

        db.commit()
        print("Seed data installed. Demo password for all seeded accounts:", PASSWORD)
    finally:
        db.close()


if __name__ == "__main__":
    main()
