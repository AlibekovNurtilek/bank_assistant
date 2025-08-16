ky_schemas = {
    "get_balance": {
        "name": "get_balance",
        "description": "Колдонуучунун  жалпы балансын алуу.",
    },
    "get_transactions": {
        "name": "get_transactions",
        "description": "Колдонуучунун акыркы транзакцияларынын тизмесин алуу (5ке чейин).",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Максималдуу транзакциялар саны (демейки 5)"},            },
            "required": []
        }
    },
    "transfer_money": {
        "name": "transfer_money",
        "description": "башка которуучуга эсеп номери боюнча акча которуу.",
        "parameters": {
            "type": "object",
            "properties": {
                "to_account_number": {"type": "string", "description": "Алуучунун  эсеп номери (IBAN)"},
                "amount": {"type": "number", "description": "Которуу суммасы"},
            },
            "required": ["to_account_number", "amount"]
        }
    },
    "get_last_incoming_transaction": {
        "name": "get_last_incoming_transaction",
        "description": "Акыркы кирген транзакция тууралуу маалымат алуу (ким акча которду жана канча).",
    },
    "get_accounts_info": {
        "name": "get_accounts_info",
        "description": "Колдонуучунун бардык эсептеринин тизмеси жана балансы.",
    },
    "get_incoming_sum_for_period": {
        "name": "get_incoming_sum_for_period",
        "description": "Көрсөтүлгөн аралыкта кирген которуулар (in) жалпы суммасы. (YYYY-MM-DD)",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Башталыш датасы (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Аякталыш датасы (YYYY-MM-DD)"},
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_outgoing_sum_for_period": {
        "name": "get_outgoing_sum_for_period",
        "description": "Көрсөтүлгөн аралыкта чыккан которуулар (out) жалпы суммасы.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Башталыш датасы (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Аякталыш датасы (YYYY-MM-DD)"},
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_last_3_transfer_recipients": {
        "name": "get_last_3_transfer_recipients",
        "description": "Акыркы 3 которуунун алуучуларынын тизмеси.",
    },
    "get_largest_transaction": {
        "name": "get_largest_transaction",
        "description": "Эң чоң транзакция (суммасы боюнча) жана анын багыты.",
    },
    "list_all_card_names": {
        "name": "list_all_card_names",
        "description": "Бардык карталардын тизмесин кайтарат.",
    },
    "get_card_details": {
        "name": "get_card_details",
        "description": "Карта аталышы боюнча бардык негизги маалыматты кайтарат (мисалы, валюта, мөөнөтү, чыгымдар, лимиттер, сүрөттөмө).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "compare_cards": {
        "name": "compare_cards",
        "description": "Карталарды негизги параметрлер боюнча салыштырат. Аргумент катары карталардын аттарынын тизмеси берилет.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_names": {
                    "type": "array", 
                    "items": {
                        "type": "string",
                        "enum": [
                            "Visa Classic Debit",
                            "Visa Gold Debit", 
                            "Visa Platinum Debit",
                            "Mastercard Standard Debit",
                            "Mastercard Gold Debit",
                            "Mastercard Platinum Debit", 
                            "Card Plus",
                            "Virtual Card",
                            "Visa Classic Credit",
                            "Visa Gold Credit",
                            "Visa Platinum Credit",
                            "Mastercard Standard Credit",
                            "Mastercard Gold Credit",
                            "Mastercard Platinum Credit",
                            "Elkart",
                            "Visa Campus Card"
                        ]
                    }, 
                    "description": "Карталардын аттарынын тизмеси (2-4 карта)"
                },
            },
            "required": ["card_names"]
        }
    },
    "get_card_limits": {
        "name": "get_card_limits",
        "description": "Карта аталышы боюнча лимиттерди кайтарат (ATM, POS, контактсыз ж.б.).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_card_benefits": {
        "name": "get_card_benefits",
        "description": "Карта аталышы боюнча артыкчылыктарды жана өзгөчөлүктөрдү кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_cards_by_type": {
        "name": "get_cards_by_type",
        "description": "Карталарды түрү боюнча фильтрлейт (дебеттик/кредиттик).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_type": {
                    "type": "string",
                    "description": "Карта түрү",
                    "enum": ["debit", "credit"]
                },
            },
            "required": ["card_type"]
        }
    },
    "get_cards_by_payment_system": {
        "name": "get_cards_by_payment_system",
        "description": "Карталарды төлөм системасы боюнча фильтрлейт (Visa/Mastercard).",
        "parameters": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "description": "Төлөм системасы",
                    "enum": ["visa", "mastercard"]
                },
            },
            "required": ["system"]
        }
    },
    "get_cards_by_fee_range": {
        "name": "get_cards_by_fee_range",
        "description": "Карталарды жылдык акы диапазону боюнча фильтрлейт.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_fee": {"type": "string", "description": "Минималдуу жылдык акы (сом)"},
                "max_fee": {"type": "string", "description": "Максималдуу жылдык акы (сом)"},
            },
            "required": []
        }
    },
    "get_cards_by_currency": {
        "name": "get_cards_by_currency",
        "description": "Карталарды валюта боюнча фильтрлейт (KGS, USD, EUR).",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Валюта",
                    "enum": ["KGS", "USD", "EUR"]
                },
            },
            "required": ["currency"]
        }
    },
    "get_card_instructions": {
        "name": "get_card_instructions",
        "description": "Картанын колдонуу көрсөтмөлөрүн кайтарат (Card Plus, Virtual Card үчүн).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Card Plus",
                        "Virtual Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_card_conditions": {
        "name": "get_card_conditions",
        "description": "Картанын шарттарын жана талаптарын кайтарат (Elkart үчүн).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": ["Elkart"]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_cards_with_features": {
        "name": "get_cards_with_features",
        "description": "Белгилүү өзгөчөлүктөргө ээ карталарды табат.",
        "parameters": {
            "type": "object",
            "properties": {
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Өзгөчөлүктөрдүн тизмеси"
                },
            },
            "required": ["features"]
        }
    },
    "get_card_recommendations": {
        "name": "get_card_recommendations",
        "description": "Критерийлерге ылайык карта сунуштарын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria": {
                    "type": "object",
                    "description": "Карта тандау критерийлери",
                    "properties": {
                        "type": {"type": "string", "description": "Карта түрү (debit/credit)", "enum": ["debit", "credit"]},
                        "max_fee": {"type": "integer", "description": "Максималдуу жылдык акы (сом)"},
                        "currency": {"type": "string", "description": "Валюта", "enum": ["KGS", "USD", "EUR"]},
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Керектүү өзгөчөлүктөр"
                        }
                    }
                },
            },
            "required": ["criteria"]
        }
    },
    "get_bank_info": {
        "name": "get_bank_info",
        "description": "Банк тууралуу негизги маалыматты кайтарат (аты, негизделген жылы, лицензия).",
    },
    "get_bank_mission": {
        "name": "get_bank_mission",
        "description": "Банктын миссиясын жана тарыхын кайтарат.",
    },
    "get_bank_values": {
        "name": "get_bank_values",
        "description": "Банктын баалуулуктарын жана принциптерин кайтарат.",
    },
    "get_ownership_info": {
        "name": "get_ownership_info",
        "description": "Банктын ээлик маалыматтарын кайтарат.",
    },
    "get_branch_network": {
        "name": "get_branch_network",
        "description": "Банктын филиалдар тармагын кайтарат.",
    },
    "get_contact_info": {
        "name": "get_contact_info",
        "description": "Банктын байланыш маалыматтарын кайтарат.",
    },
    "get_complete_about_us": {
        "name": "get_complete_about_us",
        "description": "Банк тууралуу толук маалыматты кайтарат.",
    },
    "get_about_us_section": {
        "name": "get_about_us_section",
        "description": "Банк тууралуу маалыматтын белгилүү бөлүмүн кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Маалымат бөлүмү",
                    "enum": [
                        "bank_name",
                        "founded", 
                        "license",
                        "mission",
                        "values",
                        "ownership",
                        "branches",
                        "contact",
                        "descr"
                    ]
                },
            },
            "required": ["section"]
        }
    },
    "list_all_deposit_names": {
        "name": "list_all_deposit_names",
        "description": "Бардык депозиттердин тизмесин кайтарат",
    },
    "get_deposit_details": {
        "name": "get_deposit_details",
        "description": "Депозит аталышы боюнча бардык негизги маалыматты кайтарат",
        "parameters": {
            "type": "object",
            "properties": {
                "deposit_name": {
                    "type": "string",
                    "description": "Депозиттин аталышы",
                    "enum": [
                        "Demand Deposit",
                        "Classic Term Deposit",
                        "Replenishable Deposit",
                        "Standard Term Deposit",
                        "Online Deposit",
                        "Child Deposit",
                        "Government Treasury Bills",
                        "NBKR Notes"
                    ]
                },
            },
            "required": ["deposit_name"]
        }
    },
    "compare_deposits": {
        "name": "compare_deposits",
        "description": "Депозиттерди негизги параметрлер боюнча салыштырат.",
        "parameters": {
            "type": "object",
            "properties": {
                "deposit_names": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "Demand Deposit",
                            "Classic Term Deposit",
                            "Replenishable Deposit",
                            "Standard Term Deposit",
                            "Online Deposit",
                            "Child Deposit",
                            "Government Treasury Bills",
                            "NBKR Notes"
                        ]
                    },
                    "description": "Салыштырыла турган депозиттердин аталыштары"
                },
            },
            "required": ["deposit_names"]
        }
    },
    "get_deposits_by_currency": {
        "name": "get_deposits_by_currency",
        "description": "Депозиттерди валюта боюнча фильтрлейт (KGS, USD, EUR, RUB).",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Валюта коду",
                    "enum": ["KGS", "USD", "EUR", "RUB"]
                },
            },
            "required": ["currency"]
        }
    },
    "get_deposits_by_term_range": {
        "name": "get_deposits_by_term_range",
        "description": "Депозиттерди мөөнөт диапазону боюнча фильтрлейт.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_term": {"type": "string", "description": "Минималдык мөөнөт"},
                "max_term": {"type": "string", "description": "Максималдык мөөнөт"},
            },
            "required": []
        }
    },
    "get_deposits_by_min_amount": {
        "name": "get_deposits_by_min_amount",
        "description": "Депозиттерди минималдык сумма боюнча фильтрлейт.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_amount": {"type": "string", "description": "Максималдык минималдык сумма"},
            },
            "required": ["max_amount"]
        }
    },
    "get_deposits_by_rate_range": {
        "name": "get_deposits_by_rate_range",
        "description": "Депозиттерди пайыздык ставка диапазону боюнча фильтрлейт.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_rate": {"type": "string", "description": "Минималдык пайыздык ставка"},
                "max_rate": {"type": "string", "description": "Максималдык пайыздык ставка"},
            },
            "required": []
        }
    },
    "get_deposits_with_replenishment": {
        "name": "get_deposits_with_replenishment",
        "description": "Толуктоого мүмкүндүк берген депозиттерди кайтарат.",
        
    },
    "get_deposits_with_capitalization": {
        "name": "get_deposits_with_capitalization",
        "description": "Капитализация мүмкүндүгүн берген депозиттерди кайтарат.",
    },
    "get_deposits_by_withdrawal_type": {
        "name": "get_deposits_by_withdrawal_type",
        "description": "Депозиттерди чыгаруу түрү боюнча фильтрлейт.",
        "parameters": {
            "type": "object",
            "properties": {
                "withdrawal_type": {"type": "string", "description": "Чыгаруу түрү"},
            },
            "required": ["withdrawal_type"]
        }
    },
    "get_deposit_recommendations": {
        "name": "get_deposit_recommendations",
        "description": "Критерийлерге ылайык депозит сунуштарын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria": {
                    "type": "object",
                    "description": "Сунуштук критерийлери",
                    "properties": {
                        "currency": {"type": "string", "description": "Валюта"},
                        "min_amount": {"type": "string", "description": "Минималдык сумма"},
                        "term": {"type": "string", "description": "Мөөнөт"},
                        "rate_preference": {"type": "string", "description": "Пайыздык ставка талабы"},
                        "replenishment_needed": {"type": "boolean", "description": "Толуктоо керекпи"},
                        "capitalization_needed": {"type": "boolean", "description": "Капитализация керекпи"}
                    }
                },
            },
            "required": ["criteria"]
        }
    },
    "get_government_securities": {
        "name": "get_government_securities",
        "description": "Мамлекеттик баалуу кагаздарды кайтарат (Treasury Bills, NBKR Notes).",
    },
    "get_child_deposits": {
        "name": "get_child_deposits",
        "description": "Балдар үчүн атайын депозиттерди кайтарат.",
    },
    "get_online_deposits": {
        "name": "get_online_deposits",
        "description": "Онлайн ачылуучу депозиттерди кайтарат.",
    },
    "get_faq_by_category": {
    "name": "get_faq_by_category",
    "description": "Бул инструмент  FAQ (Көп берилүүчү суроолор) маалымат базасынан жооп табуу үчүн колдонулат. LLM жоопту толугу менен FAQдагы маалыматтарга гана таянып кайтарышы керек. Жаңы маалымат ойлоп чыгарууга, өз алдынча божомол кошууга болбойт. Эгер суроого FAQ ичинде жооп жок болсо, 'Бул суроого жооп FAQ базасында жок.' деп кайтарыңыз. Жооп FAQдагы текстти өзгөртпөй кайтарылышы керек. Жооптун тили 'language' параметри менен аныкталат. Категориялар жана алардын арналуусу: \
                - 'cards' — банк карталары жөнүндө суроолор (карта алуу, жоготуу, бөгөт коюу, интернет-төлөмдөр, кредиттик лимит, коопсуздук чаралары). \
                - 'loans' — насыя жана кредиттер жөнүндө суроолор (керектүү документтер, суммасы, мөөнөтү, төлөө жолдору, мөөнөтүнөн мурда төлөө). \
                - 'internet_banking' — интернет жана мобилдик банкинг боюнча суроолор (катталуу, кирүү, пароль калыбына келтирүү, төлөмдөр, QR Pay, коопсуздук). \
                - 'deposits' — депозиттер боюнча суроолор (эсеп ачуу, пайыздык чендер, мөөнөтүнөн мурда жабуу, депозитти коргоо). \
                - 'taxes_fines' — салыктар жана айып пулдар боюнча суроолор (онлайн төлөө, текшерүү, жеңилдик мөөнөтү). \
                - 'other' — банкка тиешелүү башка суроолор (филиалдардын иш убактысы, акча которуу, байланыш номерлери, сейф ячейкалары).",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "FAQдагы категория. Жооп издөө үчүн ушул категориядагы суроо-жооптор гана колдонулат.",
                "enum": ["cards", "loans", "internet_banking", "deposits", "taxes_fines", "other"]
            },
            "question": {
                "type": "string",
                "description": "Колдонуучу берген суроо. Суроо FAQ ичиндеги суроолор менен салыштырылып, эң окшош жооп кайтарылат."
            }
        },
        "required": ["category"]
    }
}
}


ru_schemas = {
    "get_balance": {
        "name": "get_balance",
        "description": "Получить общий баланс пользователя.",
    },
    "get_transactions": {
        "name": "get_transactions",
        "description": "Получить список последних транзакций пользователя (до 5).",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Максимальное количество транзакций (по умолчанию 5)"},            
            },
            "required": []
        }
    },
    "transfer_money": {
        "name": "transfer_money",
        "description": "Перевести деньги другому пользователю по имени.",
        "parameters": {
            "type": "object",
            "properties": {
                "to_name": {"type": "string", "description": "Имя получателя"},
                "amount": {"type": "number", "description": "Сумма перевода"},
            },
            "required": ["to_name"]
        }
    },
    "get_last_incoming_transaction": {
        "name": "get_last_incoming_transaction",
        "description": "Получить информацию о последней входящей транзакции (кто перевёл деньги и сколько).",
    },
    "get_accounts_info": {
        "name": "get_accounts_info",
        "description": "Список всех счетов пользователя и их баланс.",
    },
    "get_incoming_sum_for_period": {
        "name": "get_incoming_sum_for_period",
        "description": "Общая сумма входящих переводов за указанный период.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Дата начала (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Дата окончания (YYYY-MM-DD)"},
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_outgoing_sum_for_period": {
        "name": "get_outgoing_sum_for_period",
        "description": "Общая сумма исходящих переводов за указанный период.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Дата начала (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Дата окончания (YYYY-MM-DD)"},
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_last_3_transfer_recipients": {
        "name": "get_last_3_transfer_recipients",
        "description": "Список получателей последних 3 переводов.",
    },
    "get_largest_transaction": {
        "name": "get_largest_transaction",
        "description": "Самая крупная транзакция (по сумме) и её направление.",
    },
    "list_all_card_names": {
        "name": "list_all_card_names",
        "description": "Возвращает список всех карт.",
    },
    "get_card_details": {
        "name": "get_card_details",
        "description": "Возвращает основную информацию о карте по её названию (например, валюта, срок действия, расходы, лимиты, описание).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Название карты",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "compare_cards": {
        "name": "compare_cards",
        "description": "Сравнивает карты по основным параметрам. В аргумент передаётся список названий карт.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_names": {
                    "type": "array", 
                    "items": {
                        "type": "string",
                        "enum": [
                            "Visa Classic Debit",
                            "Visa Gold Debit", 
                            "Visa Platinum Debit",
                            "Mastercard Standard Debit",
                            "Mastercard Gold Debit",
                            "Mastercard Platinum Debit", 
                            "Card Plus",
                            "Virtual Card",
                            "Visa Classic Credit",
                            "Visa Gold Credit",
                            "Visa Platinum Credit",
                            "Mastercard Standard Credit",
                            "Mastercard Gold Credit",
                            "Mastercard Platinum Credit",
                            "Elkart",
                            "Visa Campus Card"
                        ]
                    }, 
                    "description": "Список названий карт (2–4 карты)"
                },
            },
            "required": ["card_names"]
        }
    },
    "get_card_limits": {
        "name": "get_card_limits",
        "description": "Возвращает лимиты по карте (ATM, POS, бесконтактные и др.).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Название карты",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_card_benefits": {
        "name": "get_card_benefits",
        "description": "Возвращает преимущества и особенности карты по её названию.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Название карты",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_cards_by_type": {
        "name": "get_cards_by_type",
        "description": "Фильтрует карты по типу (дебетовая/кредитная).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_type": {
                    "type": "string",
                    "description": "Тип карты",
                    "enum": ["debit", "credit"]
                },
            },
            "required": ["card_type"]
        }
    },
    "get_cards_by_payment_system": {
        "name": "get_cards_by_payment_system",
        "description": "Фильтрует карты по платёжной системе (Visa/Mastercard).",
        "parameters": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "description": "Платёжная система",
                    "enum": ["visa", "mastercard"]
                },
            },
            "required": ["system"]
        }
    },
    "get_cards_by_fee_range": {
        "name": "get_cards_by_fee_range",
        "description": "Фильтрует карты по диапазону годового обслуживания.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_fee": {"type": "string", "description": "Минимальное годовое обслуживание (сом)"},
                "max_fee": {"type": "string", "description": "Максимальное годовое обслуживание (сом)"},
            },
            "required": []
        }
    },
    "get_cards_by_currency": {
        "name": "get_cards_by_currency",
        "description": "Фильтрует карты по валюте (KGS, USD, EUR).",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Валюта",
                    "enum": ["KGS", "USD", "EUR"]
                },
            },
            "required": ["currency"]
        }
    },
    "get_card_instructions": {
        "name": "get_card_instructions",
        "description": "Возвращает инструкции по использованию карты (Card Plus, Virtual Card).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Название карты",
                    "enum": [
                        "Card Plus",
                        "Virtual Card"
                    ]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_card_conditions": {
        "name": "get_card_conditions",
        "description": "Возвращает условия и требования по карте (для Elkart).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Название карты",
                    "enum": ["Elkart"]
                },
            },
            "required": ["card_name"]
        }
    },
    "get_cards_with_features": {
        "name": "get_cards_with_features",
        "description": "Находит карты с определёнными характеристиками.",
        "parameters": {
            "type": "object",
            "properties": {
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список характеристик"
                },
            },
            "required": ["features"]
        }
    },
    "get_card_recommendations": {
        "name": "get_card_recommendations",
        "description": "Возвращает рекомендации по картам в зависимости от критериев.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria": {
                    "type": "object",
                    "description": "Критерии выбора карты",
                    "properties": {
                        "type": {"type": "string", "description": "Тип карты (debit/credit)", "enum": ["debit", "credit"]},
                        "max_fee": {"type": "integer", "description": "Максимальное годовое обслуживание (сом)"},
                        "currency": {"type": "string", "description": "Валюта", "enum": ["KGS", "USD", "EUR"]},
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Необходимые характеристики"
                        }
                    }
                },
            },
            "required": ["criteria"]
        }
    },
    "get_bank_info": {
        "name": "get_bank_info",
        "description": "Возвращает основную информацию о банке (название, год основания, лицензия).",
    },
    "get_bank_mission": {
        "name": "get_bank_mission",
        "description": "Возвращает миссию и историю банка.",
    },
    "get_bank_values": {
        "name": "get_bank_values",
        "description": "Возвращает ценности и принципы банка.",
    },
    "get_ownership_info": {
        "name": "get_ownership_info",
        "description": "Возвращает информацию о владельцах банка.",
    },
    "get_branch_network": {
        "name": "get_branch_network",
        "description": "Возвращает информацию о филиальной сети банка.",
    },
    "get_contact_info": {
        "name": "get_contact_info",
        "description": "Возвращает контактную информацию банка.",
    },
    "get_complete_about_us": {
        "name": "get_complete_about_us",
        "description": "Возвращает полную информацию о банке.",
    },
    "get_about_us_section": {
        "name": "get_about_us_section",
        "description": "Возвращает определённый раздел информации о банке.",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Раздел информации",
                    "enum": [
                        "bank_name",
                        "founded", 
                        "license",
                        "mission",
                        "values",
                        "ownership",
                        "branches",
                        "contact",
                        "descr"
                    ]
                },
            },
            "required": ["section"]
        }
    },
    "list_all_deposit_names": {
        "name": "list_all_deposit_names",
        "description": "Возвращает список всех депозитов",
    },
    "get_deposit_details": {
        "name": "get_deposit_details",
        "description": "Возвращает основную информацию о депозите по его названию",
        "parameters": {
            "type": "object",
            "properties": {
                "deposit_name": {
                    "type": "string",
                    "description": "Название депозита",
                    "enum": [
                        "Demand Deposit",
                        "Classic Term Deposit",
                        "Replenishable Deposit",
                        "Standard Term Deposit",
                        "Online Deposit",
                        "Child Deposit",
                        "Government Treasury Bills",
                        "NBKR Notes"
                    ]
                },
            },
            "required": ["deposit_name"]
        }
    },
    "compare_deposits": {
        "name": "compare_deposits",
        "description": "Сравнивает депозиты по основным параметрам.",
        "parameters": {
            "type": "object",
            "properties": {
                "deposit_names": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "Demand Deposit",
                            "Classic Term Deposit",
                            "Replenishable Deposit",
                            "Standard Term Deposit",
                            "Online Deposit",
                            "Child Deposit",
                            "Government Treasury Bills",
                            "NBKR Notes"
                        ]
                    },
                    "description": "Названия депозитов для сравнения"
                },
            },
            "required": ["deposit_names"]
        }
    },
    "get_deposits_by_currency": {
        "name": "get_deposits_by_currency",
        "description": "Фильтрует депозиты по валюте (KGS, USD, EUR, RUB).",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Код валюты",
                    "enum": ["KGS", "USD", "EUR", "RUB"]
                },
            },
            "required": ["currency"]
        }
    },
    "get_deposits_by_term_range": {
        "name": "get_deposits_by_term_range",
        "description": "Фильтрует депозиты по диапазону сроков.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_term": {"type": "string", "description": "Минимальный срок"},
                "max_term": {"type": "string", "description": "Максимальный срок"},
            },
            "required": []
        }
    },
    "get_deposits_by_min_amount": {
        "name": "get_deposits_by_min_amount",
        "description": "Фильтрует депозиты по минимальной сумме.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_amount": {"type": "string", "description": "Максимальная минимальная сумма"},
            },
            "required": ["max_amount"]
        }
    },
    "get_deposits_by_rate_range": {
        "name": "get_deposits_by_rate_range",
        "description": "Фильтрует депозиты по диапазону процентных ставок.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_rate": {"type": "string", "description": "Минимальная процентная ставка"},
                "max_rate": {"type": "string", "description": "Максимальная процентная ставка"},
            },
            "required": []
        }
    },
    "get_deposits_with_replenishment": {
        "name": "get_deposits_with_replenishment",
        "description": "Возвращает депозиты с возможностью пополнения.",
    },
    "get_deposits_with_capitalization": {
        "name": "get_deposits_with_capitalization",
        "description": "Возвращает депозиты с возможностью капитализации.",
    },
    "get_deposits_by_withdrawal_type": {
        "name": "get_deposits_by_withdrawal_type",
        "description": "Фильтрует депозиты по типу снятия.",
        "parameters": {
            "type": "object",
            "properties": {
                "withdrawal_type": {"type": "string", "description": "Тип снятия"},
            },
            "required": ["withdrawal_type"]
        }
    },
    "get_deposit_recommendations": {
        "name": "get_deposit_recommendations",
        "description": "Возвращает рекомендации по депозитам в зависимости от критериев.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria": {
                    "type": "object",
                    "description": "Критерии рекомендаций",
                    "properties": {
                        "currency": {"type": "string", "description": "Валюта"},
                        "min_amount": {"type": "string", "description": "Минимальная сумма"},
                        "term": {"type": "string", "description": "Срок"},
                        "rate_preference": {"type": "string", "description": "Предпочтительная процентная ставка"},
                        "replenishment_needed": {"type": "boolean", "description": "Нужно ли пополнение"},
                        "capitalization_needed": {"type": "boolean", "description": "Нужна ли капитализация"}
                    }
                },
            },
            "required": ["criteria"]
        }
    },
    "get_government_securities": {
        "name": "get_government_securities",
        "description": "Возвращает государственные ценные бумаги (Treasury Bills, NBKR Notes).",
    },
    "get_child_deposits": {
        "name": "get_child_deposits",
        "description": "Возвращает специальные депозиты для детей.",
    },
    "get_online_deposits": {
        "name": "get_online_deposits",
        "description": "Возвращает депозиты, которые можно открыть онлайн.",
    },
    "get_faq_by_category": {
        "name": "get_faq_by_category",
        "description": "Этот инструмент используется для поиска ответа в базе данных FAQ (Часто задаваемые вопросы). LLM должен возвращать ответ, основываясь только на информации из FAQ. Запрещено придумывать новую информацию или делать собственные предположения. Если в FAQ нет ответа на вопрос, верните 'На этот вопрос нет ответа в базе FAQ.'. Ответ должен возвращаться без изменений текста из FAQ. Язык ответа определяется параметром 'language'. Категории и их назначение: \
                - 'cards' — вопросы о банковских картах (получение карты, потеря, блокировка, интернет-платежи, кредитный лимит, меры безопасности). \
                - 'loans' — вопросы о кредитах и займах (необходимые документы, сумма, срок, способы оплаты, досрочное погашение). \
                - 'internet_banking' — вопросы об интернет- и мобильном банкинге (регистрация, вход, восстановление пароля, платежи, QR Pay, безопасность). \
                - 'deposits' — вопросы о депозитах (открытие счёта, процентные ставки, досрочное закрытие, страхование депозитов). \
                - 'taxes_fines' — вопросы о налогах и штрафах (онлайн-оплата, проверка, льготный период). \
                - 'other' — прочие вопросы, связанные с банком (часы работы филиалов, перевод денег, контактные номера, сейфовые ячейки).",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Категория FAQ. Для поиска ответа используются только вопросы-ответы этой категории.",
                    "enum": ["cards", "loans", "internet_banking", "deposits", "taxes_fines", "other"]
                },
                "question": {
                    "type": "string",
                    "description": "Вопрос, заданный пользователем. Сравнивается с вопросами в FAQ, и возвращается наиболее похожий ответ."
                }
            },
            "required": ["category", "question"]
        }
    }
}

# helper: нормализуем код языка
def _norm_lang(language: str) -> str:
    return "ru" if (language or "").strip().lower() == "ru" else "ky"

# helper: выбираем схемы по языку
def _get_schemas(language: str):
    lang = _norm_lang(language)
    return ru_schemas if lang == "ru" else ky_schemas

def generate_function_docs(language: str = "ky") -> str:
    """
    Возвращает человекочитаемый список функций и параметров на выбранном языке.
    language: 'ky' (по умолчанию) или 'ru'
    """
    schemas = _get_schemas(language)
    lang = _norm_lang(language)

    # Локализация служебных фраз
    label_params = "Параметрлер" if lang == "ky" else "Параметры"
    no_params = "Параметрлер жок" if lang == "ky" else "Параметры отсутствуют"
    no_descr  = "Сүрөттөмө жок" if lang == "ky" else "нет описания"

    docs = []
    for fname, schema in schemas.items():
        description = schema.get("description") or no_descr
        params = schema.get("parameters", {}).get("properties", {})
        param_list = ", ".join(params.keys()) if params else no_params
        docs.append(f"\t{fname} — {description}. {label_params}: {param_list}")
    return "\n".join(docs)

def get_allowed_params(func_name: str, language: str = "ky") -> set:
    """
    Возвращает множество допустимых имён параметров для функции на выбранном языке.
    """
    schemas = _get_schemas(language)
    schema = schemas.get(func_name, {})
    return set(schema.get("parameters", {}).get("properties", {}).keys())

def cast_param_value(param_name: str, value, func_name: str, language: str = "ky"):
    """
    Кастует значение параметра к типу, определённому в схеме выбранного языка.
    Если тип не указан или каст не удался — возвращает исходное значение.
    """
    schemas = _get_schemas(language)
    schema = schemas.get(func_name, {})
    param_schema = schema.get("parameters", {}).get("properties", {}).get(param_name, {})
    param_type = param_schema.get("type")

    if param_type == "number":
        try:
            return float(value)
        except Exception:
            return value
    if param_type == "integer":
        try:
            return int(value)
        except Exception:
            return value
    if param_type == "string":
        return str(value)
    if param_type == "array":
        # Небольшая помощь: строку с запятыми превращаем в список
        if isinstance(value, str):
            return [v.strip() for v in value.split(",")]
        return list(value) if not isinstance(value, list) else value
    if param_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "y", "да", "ооба"}
        return bool(value)

    return value

