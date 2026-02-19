from app import create_app, db
from app.models import Payment
from datetime import datetime, timedelta

app = create_app()

with app.app_context():

    payment = Payment(
        name="Ravi Kumar",
        phone="9876543210",
        amount=1500,
        deadline=datetime.now() + timedelta(days=7)
    )

    db.session.add(payment)
    db.session.commit()

    print("Sample data inserted!")
