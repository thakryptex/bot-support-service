from apps.bot_user.handlers import init, history_request, auth, start, order_menu, faq_menu, question, warehouse, \
    logout, order_info, return_to_previous, page_prev, page_next, page_handler, order_refresh, faq_info, done, \
    confirm, add_question, continue_dialog, send_to_warehouse, incident, NodeHandler, incident_list, incident_info
from apps.bot_user.states import Init, Confirm, OrderMenu, Question, Start, HistoryRequest, OrderInfo, FaqMenu, \
    FaqInfo, Warehouse, Incident, IncidentList, IncidentInfo
from utils.bot import StateMachine


def add_return():
    return [
        ('^return_to_previous$', return_to_previous)
    ]


def add_pagination():
    return [
        ('^page_prev_.*?$', page_prev),
        ('^page_next_.*?$', page_next),
        ('^page_.*?$', page_handler)
    ]


def init_state_machine():
    """
    Structure: 
    'state': [(r'input', 'function_to_call'), ...], ...
    
    Для каждого стейта определяются возможные ветвления.
    В зависимости от вводных данных, мы вызываем тот или иной обработчик.
    """

    fsa = StateMachine()

    common_callbacks = [
        ('^init$', init),
        ('^request_id.*?$', history_request),
    ]
    callback_behavior = {
        Confirm.name: [
            ("^yes$", auth),
            ("^no$", start),
        ],

        Init.name: [
            ("^order_menu$", order_menu),
            ("^faq_menu$", faq_menu),
            ("^question$", question),
            ("^warehouse$", warehouse),
            ("^incident$", incident),
            ("^logout$", logout),
        ],

        OrderMenu.name: [
            ("^order_id.*?$", order_info),
        ] + add_return() + add_pagination(),

        OrderInfo.name: [
            ('^order_refresh$', order_refresh),
            ("^question$", question),
        ] + add_return(),

        FaqMenu.name: [
            ("^faq_id.*?$", faq_info),
        ] + add_return() + add_pagination(),

        FaqInfo.name: add_return(),

        Question.name: [
            ('^done$', done),
        ] + add_return(),

        HistoryRequest.name: add_return(),

        Incident.name: [
            ('^node_.*', NodeHandler),
            ('^incident_list$', incident_list)
        ],

        IncidentList.name: [
            ('^incident_id.*?$', incident_info),
        ] + add_pagination(),

        IncidentInfo.name: add_return(),

    }
    message_behavior = {
        Start.name: [
            (".*", confirm),
        ],
        Question.name: [
            (".*", add_question)
        ],
        HistoryRequest.name: [
            (".*", continue_dialog)
        ],
        Warehouse.name: [
            (".*", send_to_warehouse)
        ],
        Incident.name: [
            (".*", NodeHandler)
        ]
    }

    fsa.set_common_callbacks(common_callbacks)
    fsa.set_callback_behavior(callback_behavior)
    fsa.set_message_behavior(message_behavior)

    return fsa


state_machine = init_state_machine()
