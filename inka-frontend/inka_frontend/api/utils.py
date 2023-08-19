def get_question_answer_from_schema(card_schema, card_data):
    import random  # noqa: F401  -  made available for exec-ed code

    if isinstance(card_schema, str):
        rendering_context = locals() | card_data
        exec(card_schema, {}, rendering_context)  # noqa: S102
        question_template = rendering_context["card"]["question"]
        answer_template = rendering_context["card"]["answer"]
    else:
        question_template = card_schema["question"]
        answer_template = card_schema["answer"]
    return question_template, answer_template
