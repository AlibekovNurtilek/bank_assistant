from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastmcp import FastMCP
from typing import List, Optional
import json
import logging

# --- Async SQLAlchemy session ---
from app.db.base import SessionLocal  # async_sessionmaker(AsyncSession)
from app.db.models import Customer

# --- Доменные сервисы без БД ---
from app.services.mcp_services.common_services import *  # noqa
from app.services.mcp_services.personal_services import *  # noqa

# =====================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =====================================================================

async def _get_customer(session, customer_id: int) -> Optional[Customer]:
    return await session.get(Customer, customer_id)


# Создаём FastMCP сервер
server = FastMCP("banking-mcp-server")

# =====================================================================
# БАНКОВСКИЕ ИНСТРУМЕНТЫ (работают через Async SQLAlchemy + наши сервисы)
# Каждый тул принимает lang: str = "ky" и возвращает текст на выбранном языке
# =====================================================================

@server.tool(
    name="get_balance",
    description="Колдонуучунун бардык эсептериндеги жалпы балансты алуу. (lang: ky|ru)"
)
async def get_balance_tool(customer_id: int, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        total, msg = await get_balance(session, customer, lang=lang)
        return msg


@server.tool(
    name="get_transactions",
    description="Колдонуучунун акыркы транзакцияларынын тизмесин алуу (limit, default=5). (lang: ky|ru)"
)
async def get_transactions_tool(customer_id: int, limit: int = 5, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        txs, err = await get_transactions(session, customer, limit=limit, lang=lang)
        if err:
            return err
        if not txs:
            return "Акыркы транзакциялар табылган жок." if lang == "ky" else "Последние транзакции не найдены."
        # Форматируем человекочитаемый ответ
        title = "Акыркы транзакциялар:\n" if lang == "ky" else "Последние транзакции:\n"
        lines = []
        for t in txs:
            lines.append(f"- {t['type']}: {t['amount']:.2f} {t.get('currency','KGS')} {t['direction']}, {t['timestamp']}")
        return title + "\n".join(lines)


@server.tool(
    name="transfer_money",
    description="Башка колдонуучуга аты боюнча акча которуу. (params: to_name, amount, currency='KGS', lang: ky|ru)"
)
async def transfer_money_tool(customer_id: int, to_name: str, amount: float = 0, currency: str = "KGS", lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        ok, msg = await transfer_money(session, customer, to_name, amount, currency=currency, lang=lang)
        return msg


@server.tool(
    name="get_last_incoming_transaction",
    description="Акыркы кирген транзакция тууралуу маалымат алуу. (lang: ky|ru)"
)
async def get_last_incoming_transaction_tool(customer_id: int, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        _, msg = await get_last_incoming_transaction(session, customer, lang=lang)
        return msg


@server.tool(
    name="get_accounts_info",
    description="Колдонуучунун бардык эсептеринин тизмеси жана балансы. (lang: ky|ru)"
)
async def get_accounts_info_tool(customer_id: int, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        accounts, err = await get_accounts_info(session, customer, lang=lang)
        if err:
            return err
        if not accounts:
            return "Сиздин банк эсебиңиз табылган жок." if lang == "ky" else "Ваши банковские счета не найдены."
        title = "Сиздин эсептериңиз:\n" if lang == "ky" else "Ваши счета:\n"
        lines = []
        for acc in accounts:
            lines.append(f"- {acc['account_type']} {acc['account_number']}: {acc['balance']:.2f} {acc.get('currency','KGS')} ({acc['status']})")
        return title + "\n".join(lines)


@server.tool(
    name="get_incoming_sum_for_period",
    description="Көрсөтүлгөн аралыкта кирген которуулар (входящие) жалпы суммасы. (YYYY-MM-DD, YYYY-MM-DD; lang: ky|ru)"
)
async def get_incoming_sum_for_period_tool(customer_id: int, start_date: str, end_date: str, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        total, msg = await get_incoming_sum_for_period(session, customer, start_date, end_date, lang=lang)
        return msg


@server.tool(
    name="get_outgoing_sum_for_period",
    description="Көрсөтүлгөн аралыкта чыккан которуулар (исходящие) жалпы суммасы. (YYYY-MM-DD, YYYY-MM-DD; lang: ky|ru)"
)
async def get_outgoing_sum_for_period_tool(customer_id: int, start_date: str, end_date: str, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        total, msg = await get_outgoing_sum_for_period(session, customer, start_date, end_date, lang=lang)
        return msg


@server.tool(
    name="get_last_3_transfer_recipients",
    description="Акыркы 3 которуунун алуучуларынын тизмеси. (lang: ky|ru)"
)
async def get_last_3_transfer_recipients_tool(customer_id: int, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        recipients, err = await get_last_3_transfer_recipients(session, customer, lang=lang)
        if err:
            return err
        if not recipients:
            return "Акыркы алуучулар табылган жок." if lang == "ky" else "Последние получатели не найдены."
        title = "Акыркы 3 алуучу:\n" if lang == "ky" else "Последние 3 получателя:\n"
        return title + "\n".join(f"- {name}" for name in recipients)


@server.tool(
    name="get_largest_transaction",
    description="Эң чоң транзакция (суммасы боюнча) жана анын багыты. (lang: ky|ru)"
)
async def get_largest_transaction_tool(customer_id: int, lang: str = "ky"):
    async with SessionLocal() as session:
        customer = await _get_customer(session, customer_id)
        if not customer:
            return "Колдонуучу табылган жок." if lang == "ky" else "Пользователь не найден."
        tx, err = await get_largest_transaction(session, customer, lang=lang)
        if err:
            return err
        if not tx:
            return "Транзакциялар табылган жок." if lang == "ky" else "Транзакции не найдены."
        return (
            ("Эң чоң транзакция: " if lang == "ky" else "Крупнейшая транзакция: ")
            + f"{tx['amount']:.2f} {tx.get('currency','KGS')} {tx['direction']}, {tx['timestamp']}"
        )


# =====================================================================
# КАРТЫ / ДЕПОЗИТЫ / FAQ — эти сервисы не требуют БД, оставляем как есть
# =====================================================================

@server.tool(
    name="list_all_card_names",
    description="DemirBank'тагы бардык карталардын тизмесин кайтарат"
)
async def list_all_card_names_tool():
    result = list_all_card_names()
    return "".join(f"Карта аты: {card['name']}\n" for card in result)


@server.tool(
    name="get_card_details",
    description="Карта аталышы боюнча бардык негизги маалыматты кайтарат (валюта, мөөнөтү, чыгымдар, лимиттер, сүрөттөмө)."
)
async def get_card_details_tool(card_name: str):
    result = get_card_details(card_name)
    if "error" in result:
        return result["error"]
    return "\n".join(f"{k}: {v}" for k, v in result.items())


@server.tool(
    name="compare_cards",
    description="Карталарды негизги параметрлер боюнча салыштырат. Аргумент катары карталардын аттарынын тизмеси берилет (2-4 карта)."
)
async def compare_cards_tool(card_names: List[str]):
    cards = compare_cards(card_names)
    if len(cards) < 2:
        return "Карта салыштыруу үчүн эң азы 2 карта керек."

    # Список карт
    result_text = "📋 Салыштырылган карталар:\n" + "\n".join(f"{i}. {c['name']}" for i, c in enumerate(cards, 1)) + "\n\n"

    # Полное сравнение
    all_keys = set(k for c in cards for k in c.keys() if k != "name")
    similarities, differences = [], []
    for key in all_keys:
        vals = []
        for c in cards:
            v = c.get(key, "белгисиз")
            if isinstance(v, list):
                v = ", ".join(v)
            elif isinstance(v, dict):
                v = json.dumps(v, ensure_ascii=False)
            vals.append(v)
        if len(set(vals)) == 1:
            similarities.append((key, vals[0]))
        else:
            differences.append((key, [f"{c['name']}: {v}" for c, v in zip(cards, vals)]))

    result_text += "✅ Окшоштуктары:\n" + ("\n".join(f"• {k}: {v}" for k, v in similarities) or "• Жок") + "\n"
    result_text += "⚖️ Айырмачылыктары:\n"
    if differences:
        for k, infos in differences:
            result_text += f"• {k}:\n" + "\n".join(f"  - {info}" for info in infos) + "\n"
    else:
        result_text += "• Жок\n"
    return result_text


@server.tool(
    name="get_card_limits",
    description="Карта аталышы боюнча лимиттерди кайтарат (ATM, POS, контактсыз ж.б.)."
)
async def get_card_limits_tool(card_name: str):
    result = get_card_limits(card_name)
    if "error" in result:
        return result["error"]
    return json.dumps(result, ensure_ascii=False, indent=2)


@server.tool(
    name="get_card_benefits",
    description="Карта аталышы боюнча артыкчылыктарды жана өзгөчөлүктөрдү кайтарат."
)
async def get_card_benefits_tool(card_name: str):
    result = get_card_benefits(card_name)
    return json.dumps(result, ensure_ascii=False, indent=2)


@server.tool(
    name="get_cards_by_type",
    description="Карталарды түрү боюнча фильтрлейт (дебеттик/кредиттик)."
)
async def get_cards_by_type_tool(card_type: str):
    result = get_cards_by_type(card_type)
    return "📋 " + card_type.title() + " карталары:\n\n" + "\n".join(f"• {c['name']}" for c in result)


@server.tool(
    name="get_cards_by_payment_system",
    description="Карталарды төлөм системасы боюнча фильтрлейт (Visa/Mastercard)."
)
async def get_cards_by_payment_system_tool(system: str):
    result = get_cards_by_payment_system(system)
    return "📋 " + system.title() + " карталары:\n\n" + "\n".join(f"• {c['name']}" for c in result)


@server.tool(
    name="get_cards_by_fee_range",
    description="Карталарды жылдык акы диапазону боюнча фильтрлейт."
)
async def get_cards_by_fee_range_tool(min_fee: str = None, max_fee: str = None):
    result = get_cards_by_fee_range(min_fee, max_fee)
    lines = ["📋 Карталар:\n"]
    for c in result:
        lines.append(f"• {c['name']}: {c.get('annual_fee','белгисиз')}")
    return "\n".join(lines)


@server.tool(
    name="get_cards_by_currency",
    description="Карталарды валюта боюнча фильтрлейт (KGS, USD, EUR)."
)
async def get_cards_by_currency_tool(currency: str):
    result = get_cards_by_currency(currency)
    return f"📋 {currency.upper()} валютасын колдогон карталар:\n\n" + "\n".join(f"• {c['name']}" for c in result)


@server.tool(
    name="get_card_instructions",
    description="Картанын колдонуу көрсөтмөлөрүн кайтарат (Card Plus, Virtual Card үчүн)."
)
async def get_card_instructions_tool(card_name: str):
    result = get_card_instructions(card_name)
    if "error" in result:
        return result["error"]
    lines = [f"📖 {card_name} картасынын көрсөтмөлөрү:\n"]
    for k, v in result.items():
        if isinstance(v, dict):
            lines.append(f"🔹 {k.title()}:")
            for sk, sv in v.items():
                lines.append(f"  • {sk}: {sv}")
        elif isinstance(v, list):
            lines.append(f"🔹 {k.title()}:")
            for item in v:
                lines.append(f"  • {item}")
        else:
            lines.append(f"🔹 {k.title()}: {v}")
    return "\n".join(lines)


@server.tool(
    name="get_card_conditions",
    description="Картанын шарттарын жана талаптарын кайтарат (Elkart үчүн)."
)
async def get_card_conditions_tool(card_name: str):
    result = get_card_conditions(card_name)
    if "error" in result:
        return result["error"]
    lines = [f"📋 {card_name} картасынын шарттары:\n"]
    for k, v in result.items():
        if isinstance(v, dict):
            lines.append(f"🔹 {k.title()}:")
            for sk, sv in v.items():
                lines.append(f"  • {sk}: {sv}")
        else:
            lines.append(f"🔹 {k.title()}: {v}")
    return "\n".join(lines)


@server.tool(
    name="get_cards_with_features",
    description="Белгилүү өзгөчөлүктөргө ээ карталарды табат."
)
async def get_cards_with_features_tool(features: List[str]):
    result = get_cards_with_features(features)
    lines = [f"📋 '{', '.join(features)}' өзгөчөлүктөрү бар карталар:\n"]
    for c in result:
        lines.append(f"• {c['name']}")
    return "\n".join(lines)


@server.tool(
    name="get_card_recommendations",
    description="Критерийлерге ылайык карта сунуштарын кайтарат."
)
async def get_card_recommendations_tool(criteria: dict):
    result = get_card_recommendations(criteria)
    lines = ["🎯 Карта сунуштары:\n"]
    for i, c in enumerate(result, 1):
        score = c.get("recommendation_score", 0)
        fee = c.get("annual_fee", "белгисиз")
        lines.append(f"{i}. {c['name']} (упай: {score})")
        lines.append(f"   Жылдык акы: {fee}")
        if "descr" in c:
            descr = c["descr"]
            if len(descr) > 100:
                descr = descr[:100] + "..."
            lines.append(f"   Сүрөттөмө: {descr}")
        lines.append("")
    return "\n".join(lines)


@server.tool(
    name="get_bank_info",
    description="Банк тууралуу негизги маалыматты кайтарат (аты, негизделген жылы, лицензия)."
)
async def get_bank_info_tool():
    result = get_bank_info()
    return (
        f"🏦 {result['bank_name']}\n\n" \
        f"📅 Негизделген: {result['founded']}\n" \
        f"📜 Лицензия: {result['license']}\n" \
        f"📝 Сүрөттөмө: {result['descr']}\n"
    )


@server.tool(
    name="get_bank_mission",
    description="Банктын миссиясын жана тарыхын кайтарат."
)
async def get_bank_mission_tool():
    return "🎯 Банктын миссиясы:\n\n" + get_bank_mission()


@server.tool(
    name="get_bank_values",
    description="Банктын баалуулуктарын жана принциптерин кайтарат."
)
async def get_bank_values_tool():
    values = get_bank_values()
    return "💎 Банктын баалуулуктары:\n\n" + "\n".join(f"{i}. {v}" for i, v in enumerate(values, 1))


@server.tool(
    name="get_ownership_info",
    description="Банктын ээлик маалыматтарын кайтарат."
)
async def get_ownership_info_tool():
    o = get_ownership_info()
    return (
        "👥 Ээлик маалыматтары:\n\n"
        f"🔹 Негизги акционер: {o.get('main_shareholder','белгисиз')}\n"
        f"🔹 Өлкө: {o.get('country','белгисиз')}\n"
        f"🔹 Ээлик пайы: {o.get('ownership_percentage','белгисиз')}\n"
    )


@server.tool(
    name="get_branch_network",
    description="Банктын филиалдар тармагын кайтарат."
)
async def get_branch_network_tool():
    b = get_branch_network()
    lines = ["🏢 Филиалдар тармагы:\n"]
    lines.append(f"🏛️ Башкы кеңсе: {b.get('head_office','белгисиз')}\n")
    regions = b.get('regions', [])
    if regions:
        lines.append("📍 Аймактык филиалдар:")
        lines.extend(f"{i}. {r}" for i, r in enumerate(regions, 1))
    return "\n".join(lines)


@server.tool(
    name="get_contact_info",
    description="Банктын байланыш маалыматтарын кайтарат."
)
async def get_contact_info_tool():
    c = get_contact_info()
    return (
        "📞 Байланыш маалыматтары:\n\n"
        f"📱 Телефон: {c.get('phone','белгисиз')}\n"
        f"📧 Электрондук почта: {c.get('email','белгисиз')}\n"
        f"📍 Дарек: {c.get('address','белгисиз')}\n"
    )


@server.tool(
    name="get_complete_about_us",
    description="Банк тууралуу толук маалыматты кайтарат."
)
async def get_complete_about_us_tool():
    data = get_complete_about_us()
    lines = [f"🏦 {data.get('bank_name','DemirBank')}\n"]
    lines.append("\n🎯 Миссия:\n" + data.get('mission','') + "\n")
    values = data.get('values', [])
    if values:
        lines.append("💎 Баалуулуктар:")
        lines.extend(f"{i}. {v}" for i, v in enumerate(values, 1))
        lines.append("")
    ownership = data.get('ownership', {})
    if ownership:
        lines.append("👥 Ээлик:")
        lines.append(f"• Негизги акционер: {ownership.get('main_shareholder','')}")
        lines.append(f"• Өлкө: {ownership.get('country','')}")
        lines.append(f"• Ээлик пайы: {ownership.get('ownership_percentage','')}")
        lines.append("")
    branches = data.get('branches', {})
    if branches:
        lines.append("🏢 Филиалдар:")
        lines.append(f"• Башкы кеңсе: {branches.get('head_office','')}")
        regs = branches.get('regions', [])
        if regs:
            lines.append("• Аймактык филиалдар:")
            lines.extend(f"  - {r}" for r in regs)
        lines.append("")
    contact = data.get('contact', {})
    if contact:
        lines.append("📞 Байланыш:")
        lines.append(f"• Телефон: {contact.get('phone','')}")
        lines.append(f"• Электрондук почта: {contact.get('email','')}")
        lines.append(f"• Дарек: {contact.get('address','')}")
    return "\n".join(lines)


@server.tool(
    name="get_about_us_section",
    description="Банк тууралуу маалыматтын белгилүү бөлүмүн кайтарат."
)
async def get_about_us_section_tool(section: str):
    data = get_about_us_section(section)
    if isinstance(data, str) and "not found" in data:
        return data
    lines = [f"📋 {section.title()}:\n"]
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                lines.append(f"🔹 {k.replace('_',' ').title()}:")
                lines.extend(f"  • {item}" for item in v)
            else:
                lines.append(f"🔹 {k.replace('_',' ').title()}: {v}")
    elif isinstance(data, list):
        lines.extend(f"{i}. {item}" for i, item in enumerate(data, 1))
    else:
        lines.append(str(data))
    return "\n".join(lines)


# =========================
# Депозиты
# =========================

@server.tool(
    name="list_all_deposit_names",
    description="DemirBank'тагы бардык депозиттердин тизмесин кайтарат"
)
async def list_all_deposit_names_tool():
    deposits = list_all_deposit_names()
    return "💰 Бардык депозиттер:\n\n" + "\n".join(f"{i}. {d['name']}" for i, d in enumerate(deposits, 1))


@server.tool(
    name="get_deposit_details",
    description="Депозит аталышы боюнча бардык негизги маалыматты кайтарат (валюта, мөөнөт, пайыздык ставка, минималдык сумма, сүрөттөмө)."
)
async def get_deposit_details_tool(deposit_name: str):
    d = get_deposit_details(deposit_name)
    if "error" in d:
        return d["error"]
    return (
        f"💰 {d['name']}\n\n"
        f"💱 Валюта: {', '.join(d.get('currency', []))}\n"
        f"💵 Минималдык сумма: {d.get('min_amount','белгисиз')}\n"
        f"⏰ Мөөнөт: {d.get('term','белгисиз')}\n"
        f"📈 Пайыздык ставка: {d.get('rate','белгисиз')}\n"
        f"💸 Чыгаруу: {d.get('withdrawal','белгисиз')}\n"
        f"➕ Толуктоо: {d.get('replenishment','белгисиз')}\n"
        f"📊 Капитализация: {d.get('capitalization','белгисиз')}\n"
        f"📝 Сүрөттөмө: {d.get('descr','белгисиз')}\n"
    )


@server.tool(
    name="compare_deposits",
    description="Депозиттерди негизги параметрлер боюнча салыштырат. Аргумент катары депозиттердин аттарынын тизмеси берилет (2-4 депозит)."
)
async def compare_deposits_tool(deposit_names: List[str]):
    deposits = compare_deposits(deposit_names)
    if len(deposits) < 2:
        return "Депозит салыштыруу үчүн эң азы 2 депозит керек."
    # Заголовок
    result_text = "📋 Салыштырылган депозиттер:\n" + "\n".join(
        f"{i}. {d['name']}" for i, d in enumerate(deposits, 1)
    ) + "\n\n"
    # Подробности
    all_keys = set(k for d in deposits for k in d.keys() if k != "name")
    for key in all_keys:
        vals = []
        for d in deposits:
            v = d.get(key, "белгисиз")
            if isinstance(v, list):
                v = ", ".join(v)
            elif isinstance(v, dict):
                v = json.dumps(v, ensure_ascii=False)
            vals.append(v)
        if len(set(vals)) == 1:
            result_text += f"✅ Бардыгы бирдей: {vals[0]}\n\n"
        else:
            for i, (d, v) in enumerate(zip(deposits, vals), 1):
                result_text += f"  {i}. {d['name']}: {v}\n"
            result_text += "\n"
    return result_text


@server.tool(
    name="get_deposits_by_currency",
    description="Депозиттерди валюта боюнча фильтрлейт (KGS, USD, EUR, RUB)."
)
async def get_deposits_by_currency_tool(currency: str):
    deposits = get_deposits_by_currency(currency)
    lines = [f"💰 {currency.upper()} валютасындагы депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Минималдык сумма: {d.get('min_amount','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposits_by_term_range",
    description="Депозиттерди мөөнөт диапазону боюнча фильтрлейт."
)
async def get_deposits_by_term_range_tool(min_term: str = None, max_term: str = None):
    deposits = get_deposits_by_term_range(min_term, max_term)
    lines = ["⏰ Мөөнөт боюнча депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposits_by_min_amount",
    description="Депозиттерди минималдык сумма боюнча фильтрлейт."
)
async def get_deposits_by_min_amount_tool(max_amount: str):
    deposits = get_deposits_by_min_amount(max_amount)
    lines = [f"💵 {max_amount} чейинки минималдык суммадагы депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Минималдык сумма: {d.get('min_amount','белгисиз')}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposits_by_rate_range",
    description="Депозиттерди пайыздык ставка диапазону боюнча фильтрлейт."
)
async def get_deposits_by_rate_range_tool(min_rate: str = None, max_rate: str = None):
    deposits = get_deposits_by_rate_range(min_rate, max_rate)
    lines = ["📈 Пайыздык ставка боюнча депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposits_with_replenishment",
    description="Толуктоого мүмкүндүк берген депозиттерди кайтарат."
)
async def get_deposits_with_replenishment_tool():
    deposits = get_deposits_with_replenishment()
    lines = ["➕ Толуктоого мүмкүндүк берген депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposits_with_capitalization",
    description="Капитализация мүмкүндүгүн берген депозиттерди кайтарат."
)
async def get_deposits_with_capitalization_tool():
    deposits = get_deposits_with_capitalization()
    lines = ["📊 Капитализация мүмкүндүгүн берген депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposits_by_withdrawal_type",
    description="Депозиттерди чыгаруу түрү боюнча фильтрлейт."
)
async def get_deposits_by_withdrawal_type_tool(withdrawal_type: str):
    deposits = get_deposits_by_withdrawal_type(withdrawal_type)
    lines = [f"💸 {withdrawal_type} чыгаруу түрүндөгү депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Чыгаруу: {d.get('withdrawal','белгисиз')}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_deposit_recommendations",
    description="Критерийлерге ылайык депозит сунуштарын кайтарат."
)
async def get_deposit_recommendations_tool(criteria: dict):
    deposits = get_deposit_recommendations(criteria)
    lines = ["🎯 Депозит сунуштары:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}")
        lines.append(f"   Минималдык сумма: {d.get('min_amount','белгисиз')}")
        if 'recommendation_score' in d:
            lines.append(f"   Сунуштук балл: {d['recommendation_score']}")
        lines.append("")
    return "\n".join(lines)


@server.tool(
    name="get_government_securities",
    description="Мамлекеттик баалуу кагаздарды кайтарат (Treasury Bills, NBKR Notes)."
)
async def get_government_securities_tool():
    securities = get_government_securities()
    lines = ["🏛️ Мамлекеттик баалуу кагаздар:\n"]
    for i, s in enumerate(securities, 1):
        lines.append(f"{i}. {s['name']}")
        lines.append(f"   Мөөнөт: {s.get('term','белгисиз')}")
        lines.append(f"   Номиналдык сумма: {s.get('nominal_amount','белгисиз')}")
        lines.append(f"   Түрү: {s.get('type','белгисиз')}")
        lines.append(f"   Чыгаруучу: {s.get('issuer','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_child_deposits",
    description="Балдар үчүн атайын депозиттерди кайтарат."
)
async def get_child_deposits_tool():
    deposits = get_child_deposits()
    lines = ["👶 Балдар үчүн депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}")
        lines.append(f"   Минималдык сумма: {d.get('min_amount','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_online_deposits",
    description="Онлайн ачылуучу депозиттерди кайтарат."
)
async def get_online_deposits_tool():
    deposits = get_online_deposits()
    lines = ["🌐 Онлайн депозиттер:\n"]
    for i, d in enumerate(deposits, 1):
        lines.append(f"{i}. {d['name']}")
        lines.append(f"   Пайыздык ставка: {d.get('rate','белгисиз')}")
        lines.append(f"   Мөөнөт: {d.get('term','белгисиз')}")
        lines.append(f"   Минималдык сумма: {d.get('min_amount','белгисиз')}\n")
    return "\n".join(lines)


@server.tool(
    name="get_faq_by_category",
    description="Жалпы суроолорго FAQ маалыматтарын колдонуу менен жооп берет. LLM тек гана FAQ маалыматтарын колдонуу керек, жаңы маалымат ойлоп чыгарбоо керек."
)
async def get_faq_by_category_tool(category: str, question: str = None):
    logging.info("FAQ category: %s", category)
    result = get_faq_by_category(category)
    return " ".join(f"Суроо: {item['question']} Жооп: {item['answer']} \n" for item in result)


if __name__ == "__main__":
    server.run()
