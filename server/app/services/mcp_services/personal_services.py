from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable, List, Tuple, Optional, Dict
from datetime import datetime, timedelta

import pytz
from sqlalchemy import select, func, or_, and_, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# --- импортируй свои модели из того места, где они у тебя лежат ---
from app.db.models import (
    Customer,
    Account,
    Transaction,
    TransactionType,
    TransactionStatus,
    AccountStatus,
)
import logging
logger = logging.getLogger(__name__)
# =============================================================
# Настройки и утилиты
# =============================================================

LOCAL_TZ = pytz.timezone("Asia/Bishkek")


def _fmt_local(dt: datetime) -> str:
    """Форматирование в часовом поясе Asia/Bishkek (YYYY-MM-DD HH:MM)."""
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    else:
        dt = dt.astimezone(pytz.utc)
    return dt.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M")


# ========================
# Локализация сообщений
# ========================

_MSG: Dict[str, Dict[str, str]] = {
    "ky": {
        "no_accounts": "Сиздин банк эсебиңиз табылган жок.",
        "total_balance": "Сиздин бардык эсептериңиздеги жалпы сумма: {total} .",
        "no_transactions": "Акыркы транзакциялар табылган жок.",
        "last_incoming_none": "Сизге акыркы убакта акча которулган эмес.",
        "incoming_last": "Сизге акыркы акчаны {sender} {amount:.2f} сом которгон ({ts}) ({description}).",
        "need_amount": "Акча которуу суммасын көрсөтүңүз.",
        "wrong_amount": "Туура эмес сумма.",
        "not_enough": "Сиздин эсебиңизде жетиштүү каражат жок.",
        "cannot_self": "Сиз өзүңүзгө которо албайсыз.",
        "user_not_found": "{name} аттуу колдонуучу табылган жок.",
        "accounts_missing": "Эсептер табылган жок.",
        "account_blocked": "Эсеп активдүү эмес.",
        "ok_transfer": "{amount:.2f} сом {to_name} аттуу адамга ийгиликтүү которулду!",
        "period_in": "{start} - {end} аралыгында кирген которуулар: {total:.2f} сом.",
        "period_out": "{start} - {end} аралыгында чыккан которуулар: {total:.2f} сом.",
    },
    "ru": {
        "no_accounts": "Ваши банковские счета не найдены.",
        "total_balance": "Сумма по всем вашим счетам: {total} .",
        "no_transactions": "Последние транзакции не найдены.",
        "last_incoming_none": "Недавно входящих переводов не было.",
        "incoming_last": "Последний входящий перевод от {sender} на {amount:.2f} сом ({ts}) ({description}).",
        "need_amount": "Укажите сумму перевода.",
        "wrong_amount": "Неверная сумма.",
        "not_enough": "Недостаточно средств на счёте.",
        "cannot_self": "Нельзя перевести самому себе.",
        "user_not_found": "Пользователь {name} не найден.",
        "accounts_missing": "Счета не найдены.",
        "account_blocked": "Счёт не активен.",
        "ok_transfer": "{amount:.2f} сом успешно переведены пользователю {to_name}!",
        "period_in": "Сумма входящих за период {start} - {end}: {total:.2f} сом.",
        "period_out": "Сумма исходящих за период {start} - {end}: {total:.2f} сом.",
    },
}


def _t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in ("ky", "ru") else "ky"
    return _MSG[lang][key].format(**kwargs)


def _full_name(c: Customer) -> str:
    parts = [c.first_name, c.last_name]
    return " ".join(p for p in parts if p)


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


# =============================================================
# Сервисные функции (Async SQLAlchemy 2.0)
# =============================================================

async def get_balance(session: AsyncSession, customer: Customer, *, lang: str = "ky") -> tuple[Optional[str], Optional[str]]:
    stmt = select(Account).where(Account.customer_id == customer.id)
    accounts = (await session.execute(stmt)).scalars().all()
    if not accounts:
        return None, _t(lang, "no_accounts")

    # Group balances by currency
    balance_by_currency = {}
    for account in accounts:
        currency = account.currency
        balance = Decimal(account.balance or 0).quantize(Decimal("0.01"))
        balance_by_currency[currency] = balance_by_currency.get(currency, Decimal("0.00")) + balance

    # Format the result as "X KGS, Y USD, ..."
    balance_str = ", ".join(f"{amount} {currency}" for currency, amount in balance_by_currency.items())
    
    return balance_str, _t(lang, "total_balance", total=balance_str)


async def get_accounts_info(session: AsyncSession, customer: Customer, *, lang: str = "ky") -> tuple[Optional[List[dict]], Optional[str]]:
    stmt = select(Account).where(Account.customer_id == customer.id)
    accounts = (await session.execute(stmt)).scalars().all()
    if not accounts:
        return None, _t(lang, "no_accounts")
    resp = [
        {
            "account_type": a.account_type.value,
            "currency": a.currency,
            "balance": float(Decimal(a.balance or 0)),
            "status": a.status.value,
            "account_number": a.account_number,
        }
        for a in accounts
    ]
    return resp, None


async def get_transactions(
    session: AsyncSession,
    customer: Customer,
    *,
    limit: int = 5,
    lang: str = "ky",
) -> tuple[List[dict] | None, Optional[str]]:
    # Все аккаунты клиента
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    # Query both outgoing and incoming transactions for the customer's accounts
    tx_stmt = (
        select(Transaction)
        .where(
            or_(
                Transaction.from_account_id.in_(acc_ids),
                Transaction.to_account_id.in_(acc_ids),
            )
        )
        .order_by(Transaction.created_at.desc())
        .limit(limit)
    )
    txs = (await session.execute(tx_stmt)).scalars().all()
    if not txs:
        return [], _t(lang, "no_transactions")

    resp: List[dict] = []
    for t in txs:
        # Determine sender (from_account_id)
        from_fullname = "белгисиз" if lang == "ky" else "неизвестно"
        if t.from_account_id:
            account_stmt = select(Account.customer_id).where(Account.id == t.from_account_id)
            customer_id = (await session.execute(account_stmt)).scalars().first()
            if customer_id:
                customer_stmt = select(Customer).where(Customer.id == customer_id)
                sender_customer = (await session.execute(customer_stmt)).scalars().first()
                if sender_customer:
                    name_parts = [sender_customer.last_name, sender_customer.first_name]
                    if sender_customer.middle_name:
                        name_parts.append(sender_customer.middle_name)
                    from_fullname = " ".join(name_parts)

        # Determine recipient (to_account_id)
        to_fullname = "белгисиз" if lang == "ky" else "неизвестно"
        if t.to_account_id:
            account_stmt = select(Account.customer_id).where(Account.id == t.to_account_id)
            customer_id = (await session.execute(account_stmt)).scalars().first()
            if customer_id:
                customer_stmt = select(Customer).where(Customer.id == customer_id)
                recipient_customer = (await session.execute(customer_stmt)).scalars().first()
                if recipient_customer:
                    name_parts = [recipient_customer.last_name, recipient_customer.first_name]
                    if recipient_customer.middle_name:
                        name_parts.append(recipient_customer.middle_name)
                    to_fullname = " ".join(name_parts)

        # Add transaction details in the requested format
        resp.append(
            {
                "amount": float(Decimal(t.amount)),
                "currency": t.currency,
                "from_fullname": from_fullname,
                "direction": "->",
                "to_fullname": to_fullname,
                "description": t.description or "",
                "timestamp": _fmt_local(t.created_at),
            }
        )
    return resp, None
async def get_last_incoming_transaction(
    session: AsyncSession, customer: Customer, *, lang: str = "ky"
) -> tuple[None, str]:
    # Get all account IDs for the customer
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    # Query the latest incoming transaction where to_account_id matches any customer account
    tx_stmt = (
        select(Transaction)
        .where(
            Transaction.to_account_id.in_(acc_ids),
            Transaction.transaction_type.in_([TransactionType.deposit, TransactionType.transfer]),
        )
        .order_by(Transaction.created_at.desc())
        .limit(1)
    )
    tx = (await session.execute(tx_stmt)).scalars().first()
    if not tx:
        return None, _t(lang, "last_incoming_none")

    # Determine sender by fetching Customer associated with from_account_id
    sender = "белгисиз" if lang == "ky" else "неизвестно"
    if tx.from_account_id:
        account_stmt = select(Account.customer_id).where(Account.id == tx.from_account_id)
        customer_id = (await session.execute(account_stmt)).scalars().first()
        if customer_id:
            customer_stmt = select(Customer).where(Customer.id == customer_id)
            sender_customer = (await session.execute(customer_stmt)).scalars().first()
            if sender_customer:
                sender = " ".join(
                    p.strip() for p in [
                        sender_customer.first_name,
                        getattr(sender_customer, "middle_name", None),
                        sender_customer.last_name,
                    ] if p
                )

    return None, _t(
        lang,
        "incoming_last",
        sender=sender,
        amount=Decimal(tx.amount),
        ts=_fmt_local(tx.created_at),
        description=tx.description or "",
    )

async def transfer_money(
    session: AsyncSession,
    from_customer: Customer,
    to_account_number: str,
    amount: Decimal | int | str = 0,
    *,
    currency: str = "KGS",
    lang: str = "ky",
) -> tuple[bool, str]:
    # --- Валидация суммы ---
    try:
        amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return False, _t(lang, "wrong_amount")
    if amount <= 0:
        return False, _t(lang, "need_amount")

    # --- Поиск получателя по номеру счета ---
    to_acc_stmt = (
        select(Account)
        .where(
            Account.account_number == to_account_number,
            Account.status == AccountStatus.active,
            Account.currency == currency,
        )
        .limit(1)
    )
    to_acc = (await session.execute(to_acc_stmt)).scalars().first()
    if not to_acc:
        return False, _t(lang, "account_not_found", account_number=to_account_number)

    # --- Проверка, что это не свой счет ---
    to_customer_stmt = select(Customer).where(Customer.id == to_acc.customer_id)
    to_customer = (await session.execute(to_customer_stmt)).scalars().first()
    if to_customer.id == from_customer.id:
        return False, _t(lang, "cannot_self")

    # --- Выбор счета отправителя (активный и по валюте) ---
    from_acc_stmt = (
        select(Account)
        .where(
            Account.customer_id == from_customer.id,
            Account.status == AccountStatus.active,
            Account.currency == currency,
        )
        # .with_for_update()  # В SQLite не работает, см. примечание ниже
        .limit(1)
    )

    # --- ВАЖНО: «умный» контекст транзакции (SAVEPOINT если уже есть транзакция) ---
    begin_ctx = session.begin_nested() if session.in_transaction() else session.begin()
    async with begin_ctx:
        from_acc = (await session.execute(from_acc_stmt)).scalars().first()
        if not from_acc:
            return False, _t(lang, "accounts_missing")
        if from_acc.status != AccountStatus.active:
            return False, _t(lang, "account_blocked")

        from_balance = Decimal(from_acc.balance or 0)
        to_balance = Decimal(to_acc.balance or 0)
        if from_balance < amount:
            return False, _t(lang, "not_enough")

        # Обновление балансов
        from_acc.balance = (from_balance - amount).quantize(Decimal("0.01"))
        to_acc.balance = (to_balance + amount).quantize(Decimal("0.01"))

        # Установка описания в зависимости от языка
        desc = "эсептер аралык акча которуу" if lang == "ky" else "перевод между счетами"
        now = datetime.utcnow()

        # Исходящая транзакция
        tx_out = Transaction(
            from_account_id=from_acc.id,
            to_account_id=to_acc.id,
            transaction_type=TransactionType.transfer,
            amount=amount,
            currency=currency,
            description=desc,
            status=TransactionStatus.completed,
            created_at=now,
            updated_at=now,
        )
        # Входящая транзакция
        tx_in = Transaction(
            from_account_id=from_acc.id,
            to_account_id=to_acc.id,
            transaction_type=TransactionType.deposit,
            amount=amount,
            currency=currency,
            description=desc,
            status=TransactionStatus.completed,
            created_at=now,
            updated_at=now,
        )
        session.add_all([tx_out, tx_in])
        await session.flush()  # если нужно получить id транзакций до выхода

    return True, _t(lang, "ok_transfer", amount=amount, to_name=_full_name(to_customer))

async def get_incoming_sum_for_period(
    session: AsyncSession,
    customer: Customer,
    start_date: str,
    end_date: str,
    *,
    lang: str = "ky",
) -> tuple[Optional[Decimal], Optional[str]]:
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    # границы дат включительно (локальное время -> UTC naive)
    start_dt_local = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt_local = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    start_dt = LOCAL_TZ.localize(start_dt_local).astimezone(pytz.utc).replace(tzinfo=None)
    end_dt = LOCAL_TZ.localize(end_dt_local).astimezone(pytz.utc).replace(tzinfo=None)
    logger.debug("Getting incoming sum for period: %s to %s", start_dt, end_dt)
    logger.debug("Account IDs: %s", acc_ids)
    logger.debug("Local start: %s, end: %s", start_dt_local, end_dt_local)
    tx_stmt = (
        select(Transaction.amount)
        .where(
            Transaction.to_account_id.in_(acc_ids),
            Transaction.created_at >= start_dt,
            Transaction.created_at <= end_dt,
        )
    )
    amounts = [Decimal(a or 0) for a in (await session.execute(tx_stmt)).scalars().all()]
    total = sum(amounts, Decimal("0.00"))
    return total, _t(lang, "period_in", start=start_date, end=end_date, total=total)


async def get_outgoing_sum_for_period(
    session: AsyncSession,
    customer: Customer,
    start_date: str,
    end_date: str,
    *,
    lang: str = "ky",
) -> tuple[Optional[Decimal], Optional[str]]:
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    start_dt_local = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt_local = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    start_dt = LOCAL_TZ.localize(start_dt_local).astimezone(pytz.utc).replace(tzinfo=None)
    end_dt = LOCAL_TZ.localize(end_dt_local).astimezone(pytz.utc).replace(tzinfo=None)

    tx_stmt = (
        select(Transaction.amount)
        .where(
            Transaction.from_account_id.in_(acc_ids),
            Transaction.created_at >= start_dt,
            Transaction.created_at <= end_dt,
        )
    )
    amounts = [Decimal(a or 0) for a in (await session.execute(tx_stmt)).scalars().all()]
    total = sum(amounts, Decimal("0.00"))
    return total, _t(lang, "period_out", start=start_date, end=end_date, total=total)


async def get_last_3_transfer_recipients(
    session: AsyncSession, customer: Customer, *, lang: str = "ky"
) -> tuple[Optional[List[str]], Optional[str]]:
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    # Берём последние исходящие переводы по нашим счетам
    tx_stmt = (
        select(Transaction)
        .where(
            Transaction.from_account_id.in_(acc_ids),
        )
        .order_by(Transaction.created_at.desc())
        .limit(10)  # небольшой буфер, потом выберем до 3 получателей
    )
    txs = (await session.execute(tx_stmt)).scalars().all()
    if not txs:
        return [], None

    recipients: List[str] = []
    for t in txs:
        recipient = "белгисиз" if lang == "ky" else "неизвестно"
        if t.to_account_id:
            account_stmt = select(Account.customer_id).where(Account.id == t.to_account_id)
            customer_id = (await session.execute(account_stmt)).scalars().first()
            if customer_id:
                customer_stmt = select(Customer).where(Customer.id == customer_id)
                recipient_customer = (await session.execute(customer_stmt)).scalars().first()
                if recipient_customer:
                    # Construct full name: last_name first_name middle_name (if exists)
                    name_parts = [recipient_customer.first_name, recipient_customer.last_name]
                    if recipient_customer.middle_name:
                        name_parts.append(recipient_customer.middle_name)
                    recipient = " ".join(name_parts)
        # Format: ФИО amount currency created_at
        recipient_info = f"{recipient} {t.amount} {t.currency} {t.description} {_fmt_local(t.created_at)}"
        recipients.append(recipient_info)
        if len(recipients) >= 3:
            break

    return recipients[:3], None


async def get_largest_transaction(
    session: AsyncSession, customer: Customer, *, lang: str = "ky"
) -> tuple[Optional[dict], Optional[str]]:
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    cond = or_(
        Transaction.from_account_id.in_(list(acc_ids)),
        Transaction.to_account_id.in_(list(acc_ids)),
    )
    tx_stmt = (
        select(Transaction)
        .where(cond)
        .order_by(Transaction.amount.desc())
        .limit(1)
    )
    tx = (await session.execute(tx_stmt)).scalars().first()
    if not tx:
        return None, _t(lang, "no_transactions")

    # Determine sender (from_account_id)
    from_fullname = "белгисиз" if lang == "ky" else "неизвестно"
    if tx.from_account_id:
        account_stmt = select(Account.customer_id).where(Account.id == tx.from_account_id)
        customer_id = (await session.execute(account_stmt)).scalars().first()
        if customer_id:
            customer_stmt = select(Customer).where(Customer.id == customer_id)
            sender_customer = (await session.execute(customer_stmt)).scalars().first()
            if sender_customer:
                name_parts = [sender_customer.first_name, sender_customer.last_name]
                if sender_customer.middle_name:
                    name_parts.append(sender_customer.middle_name)
                from_fullname = " ".join(name_parts)

    # Determine recipient (to_account_id)
    to_fullname = "белгисиз" if lang == "ky" else "неизвестно"
    if tx.to_account_id:
        account_stmt = select(Account.customer_id).where(Account.id == tx.to_account_id)
        customer_id = (await session.execute(account_stmt)).scalars().first()
        if customer_id:
            customer_stmt = select(Customer).where(Customer.id == customer_id)
            recipient_customer = (await session.execute(customer_stmt)).scalars().first()
            if recipient_customer:
                name_parts = [recipient_customer.first_name, recipient_customer.last_name]
                if recipient_customer.middle_name:
                    name_parts.append(recipient_customer.middle_name)
                to_fullname = " ".join(name_parts)

    return (
        {
            "amount": float(Decimal(tx.amount)),
            "currency": tx.currency,
            "from_fullname": from_fullname,
            "direction": "->",
            "to_fullname": to_fullname,
            "description": tx.description or "",
            "timestamp": _fmt_local(tx.created_at),
        },
        None,
    )