from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Date, DateTime, ForeignKey, Numeric, Enum, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


# ========================
# ENUM'ы — справочники значений
# ========================

class AccountType(str, enum.Enum):
    """Тип банковского счёта"""
    current = "current"       # текущий счёт
    savings = "savings"       # сберегательный
    credit = "credit"         # кредитный

class AccountStatus(str, enum.Enum):
    """Статус банковского счёта"""
    active = "active"         # активен
    frozen = "frozen"         # заморожен
    closed = "closed"         # закрыт

class CardType(str, enum.Enum):
    """Тип банковской карты"""
    debit = "debit"           # дебетовая
    credit = "credit"         # кредитная

class CardStatus(str, enum.Enum):
    """Статус карты"""
    active = "active"         # активна
    blocked = "blocked"       # заблокирована
    expired = "expired"       # истек срок

class TransactionType(str, enum.Enum):
    """Тип транзакции"""
    deposit = "deposit"       # пополнение
    withdrawal = "withdrawal" # снятие
    transfer = "transfer"     # перевод
    payment = "payment"       # оплата

class TransactionStatus(str, enum.Enum):
    """Статус транзакции"""
    pending = "pending"       # в ожидании
    completed = "completed"   # завершена
    failed = "failed"         # ошибка

class LoanType(str, enum.Enum):
    """Тип кредита"""
    personal = "personal"     # потребительский
    mortgage = "mortgage"     # ипотека
    auto = "auto"             # автокредит
    business = "business"     # бизнес-кредит

class LoanStatus(str, enum.Enum):
    """Статус кредита"""
    active = "active"         # активен
    closed = "closed"         # погашен
    defaulted = "defaulted"   # просрочен

class PaymentStatus(str, enum.Enum):
    """Статус платежа"""
    pending = "pending"       # в ожидании
    completed = "completed"   # завершен

class EmployeeRole(str, enum.Enum):
    """Роль сотрудника в системе"""
    admin = "admin"           # администратор
    manager = "manager"       # менеджер
    support = "support"       # поддержка
    auditor = "auditor"       # аудит

class ChatStatus(str, enum.Enum):
    open = "open"         # Чат активен
    closed = "closed"     # Чат закрыт
    archived = "archived" # Чат в архиве

class MessageRole(str, enum.Enum):
    user = "user"           # Сообщение от пользователя
    assistant = "assistant" # Сообщение от ассистента
    system = "system"       # Системное сообщение


# ========================
# Таблицы
# ========================

class Customer(Base):

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))  # Отчество
    birth_date: Mapped[date]
    passport_number: Mapped[str] = mapped_column(String(50), unique=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    address: Mapped[str] = mapped_column(Text)  # Полный адрес проживания/регистрации
    password_hash: Mapped[str] = mapped_column(String(255))  # Хэш пароля (не хранить в открытом виде!)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    accounts: Mapped[List["Account"]] = relationship(back_populates="customer")
    loans: Mapped[List["Loan"]] = relationship(back_populates="customer")
    chats: Mapped[List["Chat"]] = relationship(back_populates="customer")


class Account(Base):

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    account_number: Mapped[str] = mapped_column(String(34), unique=True)  # IBAN
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    currency: Mapped[str] = mapped_column(String(3))  # ISO код валюты
    balance: Mapped[Numeric] = mapped_column(Numeric(18, 2), default=0)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.active)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    customer: Mapped["Customer"] = relationship(back_populates="accounts")
    cards: Mapped[List["Card"]] = relationship(back_populates="account")

    # 🔹 Разделяем транзакции на исходящие и входящие.
    outgoing_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="from_account",
        foreign_keys="Transaction.from_account_id",
        # при необходимости можно добавить overlaps, если где-то пересекается конфигурация:
        # overlaps="incoming_transactions,to_account"
    )
    incoming_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="to_account",
        foreign_keys="Transaction.to_account_id",
        # overlaps="outgoing_transactions,from_account"
    )

class Card(Base):

    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    card_number: Mapped[str] = mapped_column(String(16), unique=True)  # В реальном банке — хранить зашифрованно
    card_type: Mapped[CardType] = mapped_column(Enum(CardType))
    expiration_date: Mapped[date]
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.active)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с аккаунтом
    account: Mapped["Account"] = relationship(back_populates="cards")


# --- Transaction ---
class Transaction(Base):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Явные источник/получатель
    from_account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id"), nullable=True, index=True
    )
    to_account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("accounts.id"), nullable=True, index=True
    )

    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    amount: Mapped[Numeric] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), default=TransactionStatus.pending
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 🔹 РАНЬШЕ было так (ТЕПЕРЬ УДАЛЯЕМ):
    # account: Mapped["Account"] = relationship(back_populates="transactions")

    # 🔹 ТЕПЕРЬ две явные связи c указанием foreign_keys:
    from_account: Mapped[Optional["Account"]] = relationship(
        "Account",
        back_populates="outgoing_transactions",
        foreign_keys=[from_account_id],
    )
    to_account: Mapped[Optional["Account"]] = relationship(
        "Account",
        back_populates="incoming_transactions",
        foreign_keys=[to_account_id],
    )



class Loan(Base):
    """
    Кредиты, выданные клиентам
    """
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    loan_type: Mapped[LoanType] = mapped_column(Enum(LoanType))
    principal_amount: Mapped[Numeric] = mapped_column(Numeric(18, 2))  # Сумма кредита
    interest_rate: Mapped[Numeric] = mapped_column(Numeric(5, 2))      # Процентная ставка
    start_date: Mapped[date]
    end_date: Mapped[date]
    status: Mapped[LoanStatus] = mapped_column(Enum(LoanStatus), default=LoanStatus.active)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    customer: Mapped["Customer"] = relationship(back_populates="loans")
    payments: Mapped[List["LoanPayment"]] = relationship(back_populates="loan")


class LoanPayment(Base):
    """
    Платежи по кредитам
    """
    __tablename__ = "loan_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"))
    amount: Mapped[Numeric] = mapped_column(Numeric(18, 2))  # Сумма платежа
    payment_date: Mapped[date]
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связь с кредитом
    loan: Mapped["Loan"] = relationship(back_populates="payments")


class Employee(Base):
    """
    Сотрудники банка (вместо таблицы users)
    """
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # Хэш пароля (не хранить в открытом виде!)
    role: Mapped[EmployeeRole] = mapped_column(Enum(EmployeeRole), default=EmployeeRole.support)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    chats: Mapped[List["Chat"]] = relationship(back_populates="agent")


class Chat(Base):
    """
    Чат между клиентом и ассистентом
    """
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"))
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))
    status: Mapped[ChatStatus] = mapped_column(Enum(ChatStatus), default=ChatStatus.open)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    messages: Mapped[List["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    customer: Mapped[Optional["Customer"]] = relationship(back_populates="chats")
    agent: Mapped[Optional["Employee"]] = relationship(back_populates="chats")


class Message(Base):
    """
    Сообщение в чате
    """
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Связь с чатом
    chat: Mapped["Chat"] = relationship(back_populates="messages")
