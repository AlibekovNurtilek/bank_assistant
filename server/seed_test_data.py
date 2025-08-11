# seed_bank_data.py
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio

# Импортируй из своих моделей (тот файл, что мы поправили на канвасе)
from app.db.base import SessionLocal  # или свой фабричный метод сессии
from app.db.models import (
    Customer, Account, Card, Transaction, Loan, LoanPayment, Employee, Chat, Message,
    AccountType, AccountStatus, CardType, CardStatus, TransactionType, TransactionStatus,
    LoanType, LoanStatus, PaymentStatus, EmployeeRole, MessageRole, ChatStatus
)

import bcrypt

def hash_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

async def seed_data(session: AsyncSession) -> None:
    # Если уже есть данные — выходим, чтобы не дублировать
    result = await session.execute(select(Customer.id).limit(1))
    if result.first():
        print("Seed skipped: customers already exist.")
        return

    now = datetime.utcnow()

    # --- Сотрудники (агенты) ---
    emp1 = Employee(username="agent_anna", password_hash=hash_password("1234"), role=EmployeeRole.manager)
    emp2 = Employee(username="agent_bek", password_hash=hash_password("1234"), role=EmployeeRole.support)
    session.add_all([emp1, emp2])
    await session.flush()  # чтобы появились id

    # =========================
    # Customer 1
    # =========================
    c1 = Customer(
        first_name="Azamat",
        last_name="Uulu",
        middle_name="Erkin",
        birth_date=date(1995, 5, 12),
        passport_number="IDKG951205",
        phone_number="+996555000001",
        email="azamat@example.com",
        address="г. Бишкек, ул. Чуй, 123, кв. 45",
        password_hash = hash_password("1234")
    )
    # Accounts
    c1_acc1 = Account(
        customer=c1,
        account_number="KG43TEST0000000000000001",
        account_type=AccountType.current,
        currency="KGS",
        balance=Decimal("12500.00"),
        status=AccountStatus.active,
    )
    c1_acc2 = Account(
        customer=c1,
        account_number="KG43TEST0000000000000002",
        account_type=AccountType.savings,
        currency="USD",
        balance=Decimal("2300.50"),
        status=AccountStatus.active,
    )
    # Cards
    c1_card1 = Card(
        account=c1_acc1,
        card_number="4268123412341234",
        card_type=CardType.debit,
        expiration_date=date.today().replace(year=date.today().year + 3),
        status=CardStatus.active,
    )
    c1_card2 = Card(
        account=c1_acc2,
        card_number="5168123412345678",
        card_type=CardType.debit,
        expiration_date=date.today().replace(year=date.today().year + 4),
        status=CardStatus.active,
    )
    # Transactions
    c1_t1 = Transaction(
        account=c1_acc1,
        transaction_type=TransactionType.deposit,
        amount=Decimal("15000.00"),
        currency="KGS",
        description="Зачисление зарплаты",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=10),
    )
    c1_t2 = Transaction(
        account=c1_acc1,
        transaction_type=TransactionType.payment,
        amount=Decimal("2000.00"),
        currency="KGS",
        description="Оплата коммунальных услуг",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=9),
    )
    c1_t3 = Transaction(
        account=c1_acc2,
        transaction_type=TransactionType.transfer,
        amount=Decimal("300.00"),
        currency="USD",
        description="Перевод на сберегательный счёт",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=7),
    )
    # Loan + payments
    c1_loan = Loan(
        customer=c1,
        loan_type=LoanType.personal,
        principal_amount=Decimal("5000.00"),
        interest_rate=Decimal("14.50"),
        start_date=date.today() - timedelta(days=120),
        end_date=date.today() + timedelta(days=245),
        status=LoanStatus.active,
    )
    c1_lp1 = LoanPayment(
        loan=c1_loan,
        amount=Decimal("450.00"),
        payment_date=date.today() - timedelta(days=90),
        status=PaymentStatus.completed,
    )
    c1_lp2 = LoanPayment(
        loan=c1_loan,
        amount=Decimal("450.00"),
        payment_date=date.today() - timedelta(days=60),
        status=PaymentStatus.completed,
    )
    # Chat + messages
    c1_chat = Chat(
        title="Вопрос по карте",
        customer=c1,
        agent=emp1,
        status=ChatStatus.open,
        created_at=now - timedelta(days=5)
    )
    c1_m1 = Message(chat=c1_chat, role=MessageRole.user, content="Здравствуйте! Карта не проходит оплату.", created_at=now - timedelta(days=5))
    c1_m2 = Message(chat=c1_chat, role=MessageRole.assistant, content="Проверяю статус карты. Попробуйте повторить через 5 минут.", created_at=now - timedelta(days=5, seconds=-30))

    # =========================
    # Customer 2
    # =========================
    c2 = Customer(
        first_name="Aigerim",
        last_name="Sadykova",
        middle_name=None,
        birth_date=date(1998, 11, 3),
        passport_number="IDKG981103",
        phone_number="+996555000002",
        email="aigerim@example.com",
        address="г. Ош, пр. Масалиева, 10",
        password_hash = hash_password("1234")
    )
    c2_acc1 = Account(
        customer=c2,
        account_number="KG43TEST0000000000000003",
        account_type=AccountType.current,
        currency="KGS",
        balance=Decimal("8200.00"),
        status=AccountStatus.active,
    )
    c2_card1 = Card(
        account=c2_acc1,
        card_number="4895123412349876",
        card_type=CardType.debit,
        expiration_date=date.today().replace(year=date.today().year + 2),
        status=CardStatus.active,
    )
    c2_t1 = Transaction(
        account=c2_acc1,
        transaction_type=TransactionType.deposit,
        amount=Decimal("9000.00"),
        currency="KGS",
        description="Стипендия",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=20),
    )
    c2_t2 = Transaction(
        account=c2_acc1,
        transaction_type=TransactionType.withdrawal,
        amount=Decimal("800.00"),
        currency="KGS",
        description="Снятие в банкомате",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=19),
    )
    c2_t3 = Transaction(
        account=c2_acc1,
        transaction_type=TransactionType.payment,
        amount=Decimal("1200.00"),
        currency="KGS",
        description="Оплата телефона",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=18),
    )
    c2_loan = Loan(
        customer=c2,
        loan_type=LoanType.auto,
        principal_amount=Decimal("12000.00"),
        interest_rate=Decimal("16.00"),
        start_date=date.today() - timedelta(days=200),
        end_date=date.today() + timedelta(days=530),
        status=LoanStatus.active,
    )
    c2_lp1 = LoanPayment(
        loan=c2_loan,
        amount=Decimal("700.00"),
        payment_date=date.today() - timedelta(days=170),
        status=PaymentStatus.completed,
    )
    c2_lp2 = LoanPayment(
        loan=c2_loan,
        amount=Decimal("700.00"),
        payment_date=date.today() - timedelta(days=140),
        status=PaymentStatus.completed,
    )
    c2_chat = Chat(
        title="Подтверждение перевода",
        customer=c2,
        agent=emp2,
        status=ChatStatus.closed,
        created_at=now - timedelta(days=15),
        updated_at=now - timedelta(days=14),
    )
    c2_m1 = Message(chat=c2_chat, role=MessageRole.user, content="Нужно подтвердить международный перевод.", created_at=now - timedelta(days=15))
    c2_m2 = Message(chat=c2_chat, role=MessageRole.assistant, content="Перевод одобрен, ожидайте зачисления в течение 1–3 дней.", created_at=now - timedelta(days=14, hours=23))

    # =========================
    # Customer 3
    # =========================
    c3 = Customer(
        first_name="Bakyt",
        last_name="Toktogulov",
        middle_name="Nurlanovich",
        birth_date=date(1989, 2, 22),
        passport_number="IDKG890222",
        phone_number="+996555000003",
        email="bakyt@example.com",
        address="г. Каракол, ул. Абдрахманова, 7",
        password_hash = hash_password("1234")
    )
    c3_acc1 = Account(
        customer=c3,
        account_number="KG43TEST0000000000000004",
        account_type=AccountType.current,
        currency="USD",
        balance=Decimal("540.00"),
        status=AccountStatus.active,
    )
    c3_acc2 = Account(
        customer=c3,
        account_number="KG43TEST0000000000000005",
        account_type=AccountType.credit,
        currency="KGS",
        balance=Decimal("0.00"),
        status=AccountStatus.frozen,
    )
    c3_card1 = Card(
        account=c3_acc1,
        card_number="4556123411112222",
        card_type=CardType.debit,
        expiration_date=date.today().replace(year=date.today().year + 1),
        status=CardStatus.active,
    )
    c3_card2 = Card(
        account=c3_acc2,
        card_number="5533123499990000",
        card_type=CardType.credit,
        expiration_date=date.today().replace(year=date.today().year + 5),
        status=CardStatus.blocked,
    )
    c3_t1 = Transaction(
        account=c3_acc1,
        transaction_type=TransactionType.deposit,
        amount=Decimal("500.00"),
        currency="USD",
        description="Пополнение счёта",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=3),
    )
    c3_t2 = Transaction(
        account=c3_acc1,
        transaction_type=TransactionType.payment,
        amount=Decimal("25.00"),
        currency="USD",
        description="Оплата подписки",
        status=TransactionStatus.completed,
        created_at=now - timedelta(days=2),
    )
    c3_t3 = Transaction(
        account=c3_acc2,
        transaction_type=TransactionType.transfer,
        amount=Decimal("1000.00"),
        currency="KGS",
        description="Перевод на кредитный счёт",
        status=TransactionStatus.pending,
        created_at=now - timedelta(days=1),
    )
    c3_chat = Chat(
        title="Почему заморожен счёт?",
        customer=c3,
        agent=emp1,
        status=ChatStatus.open,
        created_at=now - timedelta(days=1, hours=5),
    )
    c3_m1 = Message(chat=c3_chat, role=MessageRole.user, content="Здравствуйте, почему у меня заморозили счёт?", created_at=now - timedelta(days=1, hours=5))
    c3_m2 = Message(chat=c3_chat, role=MessageRole.assistant, content="Вижу проверку безопасности. Мы уведомим, как только проверка завершится.", created_at=now - timedelta(days=1, hours=4, minutes=50))

    session.add_all([
        c1, c1_acc1, c1_acc2, c1_card1, c1_card2, c1_t1, c1_t2, c1_t3, c1_loan, c1_lp1, c1_lp2, c1_chat, c1_m1, c1_m2,
        c2, c2_acc1, c2_card1, c2_t1, c2_t2, c2_t3, c2_loan, c2_lp1, c2_lp2, c2_chat, c2_m1, c2_m2,
        c3, c3_acc1, c3_acc2, c3_card1, c3_card2, c3_t1, c3_t2, c3_t3, c3_chat, c3_m1, c3_m2
    ])

    await session.commit()
    print("Seed completed.")

async def main():
    async with SessionLocal() as session:
        await seed_data(session)

if __name__ == "__main__":
    asyncio.run(main())