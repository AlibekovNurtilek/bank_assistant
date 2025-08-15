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
        "total_balance": "Сиздин бардык эсептериңиздеги жалпы сумма: {total:.2f} сом.",
        "no_transactions": "Акыркы транзакциялар табылган жок.",
        "last_incoming_none": "Сизге акыркы убакта акча которулган эмес.",
        "incoming_last": "Сизге акыркы акчаны {sender} {amount:.2f} сом которгон ({ts}).",
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
        "total_balance": "Сумма по всем вашим счетам: {total:.2f} сом.",
        "no_transactions": "Последние транзакции не найдены.",
        "last_incoming_none": "Недавно входящих переводов не было.",
        "incoming_last": "Последний входящий перевод от {sender} на {amount:.2f} сом ({ts}).",
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

async def get_balance(session: AsyncSession, customer: Customer, *, lang: str = "ky") -> tuple[Optional[Decimal], Optional[str]]:
    stmt = select(Account).where(Account.customer_id == customer.id)
    accounts = (await session.execute(stmt)).scalars().all()
    if not accounts:
        return None, _t(lang, "no_accounts")
    total = sum((Decimal(a.balance or 0) for a in accounts), Decimal("0.00"))
    return total, _t(lang, "total_balance", total=total)


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

    tx_stmt = (
        select(Transaction)
        .where(Transaction.account_id.in_(acc_ids))
        .order_by(Transaction.created_at.desc())
        .limit(limit)
    )
    txs = (await session.execute(tx_stmt)).scalars().all()
    if not txs:
        return [], _t(lang, "no_transactions")

    resp: List[dict] = []
    for t in txs:
        # направление на основе типа транзакции
        if t.transaction_type in (TransactionType.deposit,):
            direction = "<-"
        elif t.transaction_type in (TransactionType.withdrawal, TransactionType.payment):
            direction = "->"
        else:  # transfer — смотрим описание, по умолчанию считаем исходящей из своей записи
            direction = "->"
        resp.append(
            {
                "type": t.transaction_type.value,
                "amount": float(Decimal(t.amount)),
                "direction": direction,
                "timestamp": _fmt_local(t.created_at),
                "description": t.description or "",
                "status": t.status.value,
                "currency": t.currency,
            }
        )
    return resp, None


async def get_last_incoming_transaction(
    session: AsyncSession, customer: Customer, *, lang: str = "ky"
) -> tuple[None, str]:
    acc_stmt = select(Account.id).where(Account.customer_id == customer.id)
    acc_ids = [row for row in (await session.execute(acc_stmt)).scalars().all()]
    if not acc_ids:
        return None, _t(lang, "no_accounts")

    tx_stmt = (
        select(Transaction)
        .where(
            Transaction.account_id.in_(acc_ids),
            Transaction.transaction_type.in_([TransactionType.deposit, TransactionType.transfer]),
        )
        .order_by(Transaction.created_at.desc())
        .limit(1)
    )
    tx = (await session.execute(tx_stmt)).scalars().first()
    if not tx:
        return None, _t(lang, "last_incoming_none")

    # Пытаемся извлечь отправителя из описания формата: "from {sender} to {recipient}"
    sender = ""
    if tx.description and "from " in tx.description and " to " in tx.description:
        try:
            after_from = tx.description.split("from ", 1)[1]
            sender = after_from.split(" to ", 1)[0]
        except Exception:
            sender = ""
    if not sender:
        sender = "белгисиз" if lang == "ky" else "неизвестно"

    return None, _t(
        lang,
        "incoming_last",
        sender=sender,
        amount=Decimal(tx.amount),
        ts=_fmt_local(tx.created_at),
    )


async def transfer_money(
    session: AsyncSession,
    from_customer: Customer,
    to_name: str,
    amount: Decimal | int | str = 0,
    *,
    currency: str = "KGS",
    lang: str = "ky",
) -> tuple[bool, str]:
    # Валидация суммы
    try:
        amount = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return False, _t(lang, "wrong_amount")
    if amount <= 0:
        return False, _t(lang, "need_amount")

    # Поиск получателя по ФИО (first_name + last_name)
    norm = _normalize_name(to_name)
    to_user_stmt = (
        select(Customer)
        .where(
            func.lower(func.trim(func.concat(Customer.first_name, literal(" "), Customer.last_name)))
            == norm
        )
        .limit(1)
    )
    to_customer = (await session.execute(to_user_stmt)).scalars().first()
    if not to_customer:
        return False, _t(lang, "user_not_found", name=to_name)
    if to_customer.id == from_customer.id:
        return False, _t(lang, "cannot_self")

    # Выбираем активные счёта по валюте (или просто первые активные)
    from_acc_stmt = (
        select(Account)
        .where(
            Account.customer_id == from_customer.id,
            Account.status == AccountStatus.active,
            Account.currency == currency,
        )
        .with_for_update()
        .limit(1)
    )
    to_acc_stmt = (
        select(Account)
        .where(
            Account.customer_id == to_customer.id,
            Account.status == AccountStatus.active,
            Account.currency == currency,
        )
        .with_for_update()
        .limit(1)
    )

    async with session.begin():
        from_acc = (await session.execute(from_acc_stmt)).scalars().first()
        to_acc = (await session.execute(to_acc_stmt)).scalars().first()

        if not from_acc or not to_acc:
            return False, _t(lang, "accounts_missing")
        if from_acc.status != AccountStatus.active or to_acc.status != AccountStatus.active:
            return False, _t(lang, "account_blocked")

        from_balance = Decimal(from_acc.balance or 0)
        to_balance = Decimal(to_acc.balance or 0)
        if from_balance < amount:
            return False, _t(lang, "not_enough")

        # Обновляем балансы
        from_acc.balance = (from_balance - amount).quantize(Decimal("0.01"))
        to_acc.balance = (to_balance + amount).quantize(Decimal("0.01"))

        desc = f"from {_full_name(from_customer)} to {_full_name(to_customer)}"
        now = datetime.utcnow()

        # Записываем 2 транзакции: исходящую у отправителя и входящую у получателя
        tx_out = Transaction(
            account_id=from_acc.id,
            transaction_type=TransactionType.transfer,
            amount=amount,
            currency=currency,
            description=desc,
            status=TransactionStatus.completed,
            created_at=now,
            updated_at=now,
        )
        tx_in = Transaction(
            account_id=to_acc.id,
            transaction_type=TransactionType.deposit,
            amount=amount,
            currency=currency,
            description=desc,
            status=TransactionStatus.completed,
            created_at=now,
            updated_at=now,
        )
        session.add_all([tx_out, tx_in])

    # session.begin() сам закоммитит при отсутствии исключений
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

    tx_stmt = (
        select(Transaction.amount)
        .where(
            Transaction.account_id.in_(acc_ids),
            Transaction.transaction_type.in_([TransactionType.deposit, TransactionType.transfer]),
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
            Transaction.account_id.in_(acc_ids),
            Transaction.transaction_type.in_([TransactionType.withdrawal, TransactionType.transfer, TransactionType.payment]),
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
            Transaction.account_id.in_(acc_ids),
            Transaction.transaction_type == TransactionType.transfer,
        )
        .order_by(Transaction.created_at.desc())
        .limit(10)  # небольшой буфер, потом выберем до 3 получателей
    )
    txs = (await session.execute(tx_stmt)).scalars().all()
    if not txs:
        return [], None

    recipients: List[str] = []
    for t in txs:
        # Ожидаем формат описания из transfer_money(): "from A B to C D"
        rec = None
        if t.description and " to " in t.description:
            try:
                rec = t.description.split(" to ", 1)[1]
            except Exception:
                rec = None
        if rec:
            recipients.append(rec)
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

    tx_stmt = (
        select(Transaction)
        .where(Transaction.account_id.in_(acc_ids))
        .order_by(Transaction.amount.desc())
        .limit(1)
    )
    tx = (await session.execute(tx_stmt)).scalars().first()
    if not tx:
        return None, _t(lang, "no_transactions")

    if tx.transaction_type in (TransactionType.deposit,):
        direction = "<-"
    elif tx.transaction_type in (TransactionType.withdrawal, TransactionType.payment):
        direction = "->"
    else:
        direction = "->"  # для "transfer" считаем исходящей в нашей записи

    return (
        {
            "amount": float(Decimal(tx.amount)),
            "direction": direction,
            "timestamp": _fmt_local(tx.created_at),
            "type": tx.transaction_type.value,
            "description": tx.description or "",
            "currency": tx.currency,
        },
        None,
    )
