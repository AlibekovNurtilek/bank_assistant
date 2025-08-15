import json
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

KNOWLEDGE_BASE_DIR = Path(os.getenv("KNOWLEDGE_BASE_DIR", "knowledge"))

CARDS_FILENAME = "cards.json"

def load_cards_data(lang: str = "ky") -> Dict[str, Any]:
    try:
        with open(KNOWLEDGE_BASE_DIR.joinpath(lang, CARDS_FILENAME), encoding='utf-8') as f:
            cards_json = json.load(f)
            return cards_json.get('cards', {})
    except Exception as e:
        logging.exception(f"Error loading cards data: {e}")
        return {}

# 1. List all card types
def list_all_card_names(lang: str = "ky") -> List[Dict[str, str]]:
    cards = load_cards_data(lang)
    result = []
    for card in cards.values():
        result.append({
            "name": card.get("name", ""),
        })
    return result

# 2. Get card details by name
def get_card_details(card_name: str, lang: str = "ky") -> Dict[str, Any]:
    cards = load_cards_data(lang)
    for card in cards.values():
        if card.get("name", "").lower() == card_name.lower():
            return card
    return {"error": "Карта табылган жок."}

# 3. Compare cards by names
def compare_cards(card_names: List[str], lang: str = "ky") -> List[Dict[str, Any]]:
    cards = load_cards_data(lang)
    found = []
    names_lower = [n.lower() for n in card_names]
    for card in cards.values():
        if card.get("name", "").lower() in names_lower:
            found.append(card)
    return found

# 8. Get cards by annual fee range
def get_card_limits(card_name: str, lang: str = "ky") -> Dict[str, Any]:
    card = get_card_details(card_name, lang)
    if "limits" in card:
        return card["limits"]
    if "error" in card:
        return {"error": card["error"]}
    return {"error": "Лимиттер табылган жок."}

# 5. Get card benefits
def get_card_benefits(card_name: str, lang: str = "ky") -> List[str]:
    card = get_card_details(card_name, lang)
    # Try to extract benefits, instructions, notes, or descr
    benefits = []
    if "benefits" in card:
        benefits.extend(card["benefits"])
    if "Services" in card:
        benefits.extend(card["Services"])
    if "instuctions" in card:
        benefits.extend(list(card["instuctions"].values()))
    if "notes" in card:
        benefits.extend(card["notes"])
    if "descr" in card:
        benefits.append(card["descr"])
    return benefits or ["No benefits found for this card"]

# 6. Get cards by type (debit/credit)
def get_cards_by_type(card_type: str, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get cards filtered by type (debit/credit)"""
    cards = load_cards_data(lang)
    result = []
    card_type_lower = card_type.lower()
    
    for card in cards.values():
        name = card.get("name", "").lower()
        if card_type_lower in name:
            result.append(card)
    
    return result

# 7. Get cards by payment system (Visa/Mastercard)
def get_cards_by_payment_system(system: str, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get cards filtered by payment system (Visa/Mastercard)"""
    cards = load_cards_data(lang)
    result = []
    system_lower = system.lower()
    
    for card in cards.values():
        name = card.get("name", "").lower()
        if system_lower in name:
            result.append(card)
    
    return result

# 8. Get cards by annual fee range
def get_cards_by_fee_range(min_fee: str = None, max_fee: str = None, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get cards filtered by annual fee range"""
    cards = load_cards_data(lang)
    result = []
    
    for card in cards.values():
        fee = card.get("annual_fee", "")
        if fee == "акысыз":
            fee_value = 0
        elif "сом" in fee:
            try:
                fee_value = int(fee.replace(" сом", "").replace(" ", ""))
            except:
                fee_value = float('inf')
        else:
            fee_value = float('inf')
        
        # Apply filters
        if min_fee is not None:
            min_fee_value = int(min_fee) if min_fee.isdigit() else 0
            if fee_value < min_fee_value:
                continue
                
        if max_fee is not None:
            max_fee_value = int(max_fee) if max_fee.isdigit() else float('inf')
            if fee_value > max_fee_value:
                continue
        
        result.append(card)
    
    return result

# 9. Get cards by currency
def get_cards_by_currency(currency: str, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get cards that support specific currency"""
    cards = load_cards_data(lang)
    result = []
    currency_upper = currency.upper()
    
    for card in cards.values():
        card_currencies = card.get("currency", [])
        if isinstance(card_currencies, list) and currency_upper in card_currencies:
            result.append(card)
    
    return result

# 10. Get card instructions (for Card Plus and Virtual cards)
def get_card_instructions(card_name: str, lang: str = "ky") -> Dict[str, Any]:
    """Get card instructions and usage guide"""
    card = get_card_details(card_name, lang)
    if "error" in card:
        return card
    
    instructions = {}
    if "instructions" in card:
        instructions["instructions"] = card["instructions"]
    if "instuctions" in card:  # Note: typo in original data
        instructions["instructions"] = card["instuctions"]
    if "rates" in card:
        instructions["rates"] = card["rates"]
    if "notes" in card:
        instructions["notes"] = card["notes"]
    
    return instructions if instructions else {"error": "Instructions not found for this card"}

# 11. Get card conditions (for Elkart)
def get_card_conditions(card_name: str, lang: str = "ky") -> Dict[str, Any]:
    """Get card conditions and requirements"""
    card = get_card_details(card_name, lang)
    if "error" in card:
        return card
    
    if "conditions" in card:
        return card["conditions"]
    
    return {"error": "Conditions not found for this card"}

# 12. Get cards with specific features
def get_cards_with_features(features: List[str], lang: str = "ky") -> List[Dict[str, Any]]:
    """Get cards that have specific features"""
    cards = load_cards_data(lang)
    result = []
    features_lower = [f.lower() for f in features]
    
    for card in cards.values():
        card_text = str(card).lower()
        if all(feature in card_text for feature in features_lower):
            result.append(card)
    
    return result

# 13. Get best card recommendations
def get_card_recommendations(criteria: Dict[str, Any], lang: str = "ky") -> List[Dict[str, Any]]:
    """Get card recommendations based on criteria"""
    cards = load_cards_data(lang)
    result = []
    
    # Extract criteria
    card_type = criteria.get("type", "").lower()  # debit/credit
    max_fee = criteria.get("max_fee", None)
    currency = criteria.get("currency", "").upper()
    features = criteria.get("features", [])
    
    for card in cards.values():
        score = 0
        name = card.get("name", "").lower()
        
        # Type matching
        if card_type and card_type in name:
            score += 10
        
        # Fee matching
        if max_fee is not None:
            fee = card.get("annual_fee", "")
            if fee == "акысыз":
                score += 5
            elif "сом" in fee:
                try:
                    fee_value = int(fee.replace(" сом", "").replace(" ", ""))
                    if fee_value <= max_fee:
                        score += 3
                except:
                    pass
        
        # Currency matching
        if currency:
            card_currencies = card.get("currency", [])
            if isinstance(card_currencies, list) and currency in card_currencies:
                score += 5
        
        # Features matching
        if features:
            card_text = str(card).lower()
            for feature in features:
                if feature.lower() in card_text:
                    score += 2
        
        if score > 0:
            card["recommendation_score"] = score
            result.append(card)
    
    # Sort by score
    result.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
    return result[:5]  # Return top 5 recommendations

# About Us functions
ABOUT_US_FILENAME = "about-us.json"

def load_about_us_data(lang: str = "ky") -> Dict[str, Any]:
    """Load about us data from JSON file"""
    try:
        with open(KNOWLEDGE_BASE_DIR.joinpath(lang, ABOUT_US_FILENAME), encoding='utf-8') as f:
            about_us_json = json.load(f)
            return about_us_json.get('about-us', {})
    except Exception as e:
        logging.exception(f"Error loading about us data: {e}")
        return {}

# 14. Get general bank information
def get_bank_info(lang: str = "ky") -> Dict[str, Any]:
    """Get general bank information"""
    data = load_about_us_data(lang)
    return {
        "bank_name": data.get("bank_name", ""),
        "founded": data.get("founded", ""),
        "license": data.get("license", ""),
        "descr": data.get("descr", "")
    }

# 15. Get bank mission
def get_bank_mission(lang: str = "ky") -> str:
    """Get bank mission statement"""
    data = load_about_us_data(lang)
    return data.get("mission", "Mission not found")

# 16. Get bank values
def get_bank_values(lang: str = "ky") -> List[str]:
    """Get bank values and principles"""
    data = load_about_us_data(lang)
    return data.get("values", [])

# 17. Get ownership information
def get_ownership_info(lang: str = "ky") -> Dict[str, Any]:
    """Get bank ownership information"""
    data = load_about_us_data(lang)
    return data.get("ownership", {})

# 18. Get branch network information
def get_branch_network(lang: str = "ky") -> Dict[str, Any]:
    """Get bank branch network information"""
    data = load_about_us_data(lang)
    return data.get("branches", {})

# 19. Get contact information
def get_contact_info(lang: str = "ky") -> Dict[str, Any]:
    """Get bank contact information"""
    data = load_about_us_data(lang)
    return data.get("contact", {})

# 20. Get complete about us information
def get_complete_about_us(lang: str = "ky") -> Dict[str, Any]:
    """Get complete about us information"""
    return load_about_us_data(lang)

# 21. Get specific about us section
def get_about_us_section(section: str, lang: str = "ky") -> Any:
    """Get specific section of about us information"""
    data = load_about_us_data(lang)
    return data.get(section, f"Section '{section}' not found")

# Deposit functions
DEPOSITS_FILENAME = "deposits.json"

def load_deposits_data(lang: str = "ky") -> Dict[str, Any]:
    """Load deposits data from JSON file"""
    try:
        with open(KNOWLEDGE_BASE_DIR.joinpath(lang, DEPOSITS_FILENAME), encoding='utf-8') as f:
            deposits_json = json.load(f)
            return deposits_json.get('deposits', {})
    except Exception as e:
        logging.exception(f"Error loading deposits data: {e}")
        return {}

# 22. List all deposit names
def list_all_deposit_names(lang: str = "ky") -> List[Dict[str, str]]:
    """Get list of all available deposit names"""
    deposits = load_deposits_data(lang)
    result = []
    for deposit in deposits.values():
        result.append({
            "name": deposit.get("name", ""),
        })
    return result

# 23. Get deposit details by name
def get_deposit_details(deposit_name: str, lang: str = "ky") -> Dict[str, Any]:
    """Get detailed information about a specific deposit"""
    deposits = load_deposits_data(lang)
    for deposit in deposits.values():
        if deposit.get("name", "").lower() == deposit_name.lower():
            return deposit
    return {"error": "Депозит табылган жок."}

# 24. Compare deposits by names
def compare_deposits(deposit_names: List[str], lang: str = "ky") -> List[Dict[str, Any]]:
    """Compare multiple deposits by their names"""
    deposits = load_deposits_data(lang)
    found = []
    names_lower = [n.lower() for n in deposit_names]
    for deposit in deposits.values():
        if deposit.get("name", "").lower() in names_lower:
            found.append(deposit)
    return found

# 25. Get deposits by currency
def get_deposits_by_currency(currency: str, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits filtered by currency"""
    deposits = load_deposits_data(lang)
    result = []
    currency_upper = currency.upper()
    
    for deposit in deposits.values():
        currencies = deposit.get("currency", [])
        if isinstance(currencies, list) and currency_upper in currencies:
            result.append(deposit)
    
    return result

# 26. Get deposits by term range
def get_deposits_by_term_range(min_term: str = None, max_term: str = None, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits filtered by term range"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        term = deposit.get("term", "")
        if not term:
            continue
            
        # Simple term matching (can be improved with more sophisticated parsing)
        if min_term and min_term.lower() in term.lower():
            result.append(deposit)
        elif max_term and max_term.lower() in term.lower():
            result.append(deposit)
        elif not min_term and not max_term:
            result.append(deposit)
    
    return result

# 27. Get deposits by minimum amount
def get_deposits_by_min_amount(max_amount: str, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits with minimum amount less than or equal to specified amount"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        min_amount = deposit.get("min_amount", "")
        if not min_amount:
            continue
            
        # Simple amount comparison (can be improved with currency conversion)
        if max_amount.lower() in min_amount.lower():
            result.append(deposit)
    
    return result

# 28. Get deposits by rate range
def get_deposits_by_rate_range(min_rate: str = None, max_rate: str = None, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits filtered by interest rate range"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        rate = deposit.get("rate", "")
        if not rate:
            continue
            
        # Simple rate matching
        if min_rate and min_rate.lower() in rate.lower():
            result.append(deposit)
        elif max_rate and max_rate.lower() in rate.lower():
            result.append(deposit)
        elif not min_rate and not max_rate:
            result.append(deposit)
    
    return result

# 29. Get deposits with replenishment option
def get_deposits_with_replenishment(lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits that allow replenishment"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        replenishment = deposit.get("replenishment", "")
        if "ооба" in replenishment.lower() or "yes" in replenishment.lower():
            result.append(deposit)
    
    return result

# 30. Get deposits with capitalization
def get_deposits_with_capitalization(lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits that offer capitalization"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        capitalization = deposit.get("capitalization", "")
        if "ооба" in capitalization.lower() or "yes" in capitalization.lower():
            result.append(deposit)
    
    return result

# 31. Get deposits by withdrawal type
def get_deposits_by_withdrawal_type(withdrawal_type: str, lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits filtered by withdrawal type"""
    deposits = load_deposits_data(lang)
    result = []
    withdrawal_type_lower = withdrawal_type.lower()
    
    for deposit in deposits.values():
        withdrawal = deposit.get("withdrawal", "")
        if withdrawal_type_lower in withdrawal.lower():
            result.append(deposit)
    
    return result

# 32. Get deposit recommendations
def get_deposit_recommendations(criteria: Dict[str, Any], lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposit recommendations based on criteria"""
    deposits = load_deposits_data(lang)
    result = []
    
    currency = criteria.get("currency")
    min_amount = criteria.get("min_amount")
    term = criteria.get("term")
    rate_preference = criteria.get("rate_preference")
    replenishment_needed = criteria.get("replenishment_needed")
    capitalization_needed = criteria.get("capitalization_needed")
    
    for deposit in deposits.values():
        score = 0
        
        # Currency matching
        if currency:
            currencies = deposit.get("currency", [])
            if isinstance(currencies, list) and currency.upper() in currencies:
                score += 5
        
        # Amount matching
        if min_amount:
            deposit_min = deposit.get("min_amount", "")
            if min_amount.lower() in deposit_min.lower():
                score += 3
        
        # Term matching
        if term:
            deposit_term = deposit.get("term", "")
            if term.lower() in deposit_term.lower():
                score += 3
        
        # Rate preference
        if rate_preference:
            deposit_rate = deposit.get("rate", "")
            if rate_preference.lower() in deposit_rate.lower():
                score += 2
        
        # Replenishment matching
        if replenishment_needed:
            replenishment = deposit.get("replenishment", "")
            if replenishment_needed and "ооба" in replenishment.lower():
                score += 2
        
        # Capitalization matching
        if capitalization_needed:
            capitalization = deposit.get("capitalization", "")
            if capitalization_needed and "ооба" in capitalization.lower():
                score += 2
        
        if score > 0:
            deposit["recommendation_score"] = score
            result.append(deposit)
    
    # Sort by score
    result.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
    return result[:5]  # Return top 5 recommendations

# 33. Get government securities
def get_government_securities(lang: str = "ky") -> List[Dict[str, Any]]:
    """Get government securities (Treasury Bills, NBKR Notes)"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        name = deposit.get("name", "").lower()
        if "treasury" in name or "nbkr" in name or "government" in name:
            result.append(deposit)
    
    return result

# 34. Get child deposits
def get_child_deposits(lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits specifically designed for children"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        name = deposit.get("name", "").lower()
        if "child" in name or "бала" in name:
            result.append(deposit)
    
    return result

# 35. Get online deposits
def get_online_deposits(lang: str = "ky") -> List[Dict[str, Any]]:
    """Get deposits that can be opened online"""
    deposits = load_deposits_data(lang)
    result = []
    
    for deposit in deposits.values():
        name = deposit.get("name", "").lower()
        if "online" in name:
            result.append(deposit)
    
    return result

# FAQ functions
FAQ_FILENAME = "useful-info.json"

def load_faq_data(lang: str = "ky") -> Dict[str, List[Dict[str, str]]]:
    """Load FAQ data from JSON file"""
    try:
        with open(KNOWLEDGE_BASE_DIR.joinpath(lang, FAQ_FILENAME), encoding='utf-8') as f:
            data = json.load(f)
            return data.get('useful-info', {})
    except Exception as e:
        logging.exception(f"Error loading FAQ data: {e}")
        return {}

def get_faq_by_category(category: str, lang: str = "ky") -> str:
    print("-------------------get_faq_by_category--------------------------")
    """Answer general questions using FAQ data"""
    data = load_faq_data(lang)
    for category_name in data.keys():
        if category_name.lower() == category.lower():
            return data.get(category_name, [])
    return "Категория табылган жок."