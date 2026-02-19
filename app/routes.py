from unicodedata import name
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.models import Payment
from flask import flash
from utils import email_service
from utils.email_service import EmailService

from utils.fast2sms_service import Fast2SMSService

from app import db
from datetime import datetime

main = Blueprint("main", __name__)


# Home / Dashboard
@main.route("/")
def home():
    from datetime import datetime

    payments = Payment.query.order_by(Payment.created_at.desc()).all()

    today = datetime.now().date()

    for p in payments:
       if p.deadline.date() < today and p.status == "Pending":
        p.is_overdue = True
       else:
        p.is_overdue = False

    return render_template("dashboard.html", payments=payments)


# Add new payment
@main.route("/add", methods=["POST"])
def add_payment():

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    amount = request.form.get("amount")
    deadline = request.form.get("deadline")


    if not all([name, email, amount, deadline]):

         flash("All fields are required!", "danger")
         return redirect(url_for("main.home"))


    try:
        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
        amount = float(amount)
    except:
        flash("Invalid data format!", "danger")
        return redirect(url_for("main.home"))
    # Check if same person exists
    existing = Payment.query.filter_by(
    name=name,
    email=email,
    status="Pending"
      ).first()


    if existing:

    # Merge amount
         existing.amount += amount

    # Update deadline
         if deadline_date > existing.deadline:
           existing.deadline = deadline_date

         db.session.commit()

    # Send updated email
         email_service = EmailService()

         subject = "Updated Payment Amount"

         message = f"""
Hello {name},

Your payment record has been updated.

New Total Amount: ₹{existing.amount}
New Deadline: {existing.deadline.strftime('%Y-%m-%d')}

Please clear before deadline.

Thank you.
"""

         email_service.send_email(email, subject, message)

         flash("Existing payment updated & Email sent!", "success")

         return redirect(url_for("main.home"))

    else:

     payment = Payment(
        name=name,
        phone=phone,
        email=email,
        amount=amount,
        deadline=deadline_date,
        status="Pending"
    )



    db.session.add(payment)
    db.session.commit()

# Send Email Notification
    email_service = EmailService()

    subject = "Payment Reminder"

    message = f"""
    Hello {name},

    You borrowed ₹{amount}.
    Please return before {deadline}.

    Thank you.
    """

    email_status = email_service.send_email(email, subject, message)


    if email_status:
      flash("Payment added & Email sent successfully!", "success")
    else:
        flash("Payment added but Email failed!", "warning")


    return redirect(url_for("main.home"))


# List all payments (API)
@main.route("/list")
def list_payments():

    payments = Payment.query.all()

    result = []

    for p in payments:
        result.append({
            "id": p.id,
            "name": p.name,
            "phone": p.phone,
            "amount": p.amount,
            "deadline": p.deadline.strftime("%Y-%m-%d"),
            "status": p.status
        })

    return jsonify(result)


# Delete entry
@main.route("/delete/<int:id>")
def delete_payment(id):

    payment = Payment.query.get_or_404(id)

    email_service = EmailService()

    subject = "Payment Completed"

    message = f"""
Hello {payment.name},

Your payment of ₹{payment.amount} has been completed.

Status: Paid
Deadline: {payment.deadline.strftime('%Y-%m-%d')}

Thank you for clearing the dues.

Regards.
"""

    email_service.send_email(payment.email, subject, message)

    db.session.delete(payment)
    db.session.commit()

    flash("Payment removed & Email sent!", "success")

    return redirect(url_for("main.home"))




# Mark as Paid
@main.route("/mark-paid/<int:id>")
def mark_paid(id):

    payment = Payment.query.get_or_404(id)

    payment.status = "Paid"

    db.session.commit()
    flash("Marked as Paid!", "success")

    return redirect(url_for("main.home"))


@main.route("/alert/<int:id>")
def send_alert(id):

    payment = Payment.query.get_or_404(id)

    email_service = EmailService()

    subject = "Payment Reminder - Overdue"

    message = f"""
Hello {payment.name},

Your payment of ₹{payment.amount} is overdue.

Original Deadline: {payment.deadline.strftime('%Y-%m-%d')}

Please clear it soon.

If deadline is extended, contact me.

Thank you.
"""

    email_service.send_email(payment.email, subject, message)

    flash("Reminder Email Sent!", "info")

    return redirect(url_for("main.home"))


@main.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_payment(id):

    payment = Payment.query.get_or_404(id)

    if request.method == "POST":

        paid = request.form.get("paid")
        new_deadline = request.form.get("deadline")

        email_service = EmailService()

        # Partial Payment Logic
        if paid and float(paid) > 0:

            paid = float(paid)

            if paid >= payment.amount:
                payment.amount = 0
                payment.status = "Paid"

            else:
                payment.amount -= paid

        # Deadline Extension
        if new_deadline:
            payment.deadline = datetime.strptime(new_deadline, "%Y-%m-%d")

        db.session.commit()

        # Send Balance Email
        subject = "Payment Updated"

        message = f"""
Hello {payment.name},

Your payment has been updated.

Remaining Amount: ₹{payment.amount}
New Deadline: {payment.deadline.strftime('%Y-%m-%d')}

Please clear balance before deadline.

Thank you.
"""

        email_service.send_email(payment.email, subject, message)

        flash("Payment updated & Email sent!", "success")

        return redirect(url_for("main.home"))

    return render_template("edit_payment.html", p=payment)
