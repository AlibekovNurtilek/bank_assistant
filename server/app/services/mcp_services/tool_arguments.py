tools_params = {
    "get_balance": ["customer_id", "lang"],
    "get_transactions": ["customer_id", "limit", "lang"],
    "transfer_money": ["customer_id", "to_name", "amount", "currency", "lang"],
    "get_last_incoming_transaction": ["customer_id", "lang"],
    "get_accounts_info": ["customer_id", "lang"],
    "get_incoming_sum_for_period": ["customer_id", "start_date", "end_date", "lang"],
    "get_outgoing_sum_for_period": ["customer_id", "start_date", "end_date", "lang"],
    "get_last_3_transfer_recipients": ["customer_id", "lang"],
    "get_largest_transaction": ["customer_id", "lang"],
    "list_all_card_names": [],
    "get_card_details": ["card_name"],
    "compare_cards": ["card_names"],
    "get_card_limits": ["card_name"],
    "get_card_benefits": ["card_name"],
    "get_cards_by_type": ["card_type"],
    "get_cards_by_payment_system": ["system"],
    "get_cards_by_fee_range": ["min_fee", "max_fee"],
    "get_cards_by_currency": ["currency"],
    "get_card_instructions": ["card_name"],
    "get_card_conditions": ["card_name"],
    "get_cards_with_features": ["features"],
    "get_card_recommendations": ["criteria"],
    "get_bank_info": [],
    "get_bank_mission": [],
    "get_bank_values": [],
    "get_ownership_info": [],
    "get_branch_network": [],
    "get_contact_info": [],
    "get_complete_about_us": [],
    "get_about_us_section": ["section"],
    "list_all_deposit_names": [],
    "get_deposit_details": ["deposit_name"],
    "compare_deposits": ["deposit_names"],
    "get_deposits_by_currency": ["currency"],
    "get_deposits_by_term_range": ["min_term", "max_term"],
    "get_deposits_by_min_amount": ["max_amount"],
    "get_deposits_by_rate_range": ["min_rate", "max_rate"],
    "get_deposits_with_replenishment": [],
    "get_deposits_with_capitalization": [],
    "get_deposits_by_withdrawal_type": ["withdrawal_type"],
    "get_deposit_recommendations": ["criteria"],
    "get_government_securities": [],
    "get_child_deposits": [],
    "get_online_deposits": [],
    "get_faq_by_category": ["category"]
}


def filter_tool_args(name: str, kwargs: dict) -> list:
    """
    Фильтрует входящие аргументы по списку допустимых для тула.
    Возвращает список значений в порядке, указанном в tools_params.
    """
    valid_params = tools_params.get(name, [])
    return {k: v for k, v in kwargs.items() if k in valid_params}