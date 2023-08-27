import random
from abc import ABC, abstractmethod
from typing import Dict

from jinja2 import Template, Environment

from inka_api.api.utils import get_question_answer_from_schema
from inka_frontend.app import get_jinja2

import base64


def render_card(card_schema, card_data):
    return Template(card_schema).render(**card_data, **get_jinja2().globals)


class Algorithm(ABC):
    def buttons(self):
        return {
            "correct": "var(--success)",
            "wrong": "var(--danger)",
        }

    @abstractmethod
    def next_card(self, deck, schemas):
        ...

    @abstractmethod
    def process_result(self, deck, card_id, card_type, result):
        ...


class Random(Algorithm):
    """
    Picks a random card from the deck.
    No review data is kept.
    """

    def next_card(self, deck, schemas):
        card_id, card_data = random.choice(list(deck["cards"].items()))
        card_schema = schemas[card_data["schema"]]
        card_type, card = random.choice(list(card_schema["cards"].items()))
        question = render_card(card["question"], card_data) #Template(card["question"]).render(**card_data)
        answer = render_card(card["answer"], card_data) #Template(card["answer"]).render(**card_data)
        return card_id, card_type, question, answer

    def process_result(self, deck, card_id, card_type, result):
        pass


class HardestFirst(Algorithm):
    """
    For each successful reviews adds 1 to the score.
    For each failed review, sets the score to the minimum of all scores minus 1.
    The algorithm picks a random card with a score below [minimum + 3].
    """

    def buttons(self):
        return {
            "correct": "var(--success)",
            "wrong": "var(--danger)",
        }

    def next_card(self, deck, schemas, from_minimum=3):
        """
        from_minimum: how many values above the minimum are still considered
            when selecting the cards to pick from.
            Default: 3
        """
        reviewable_cards = [
            (card_id, card_type, review_data or 0)
            for card_id, card_data in deck["cards"].items()
            for card_type, review_data in card_data["reviews"].items()
            if card_type in schemas[card_data["schema"]]["cards"]
        ]
        reviewable_cards.sort(key=lambda x: x[2])
        threshold = reviewable_cards[0][2] + from_minimum
        cards_to_pick_from = [
            reviewable_card
            for reviewable_card in reviewable_cards
            if reviewable_card[2] <= threshold
        ]

        card_id, card_type, _ = random.choice(cards_to_pick_from)
        card_schema = schemas[deck["cards"][card_id]["schema"]]["cards"][card_type]

        question_template, answer_template = get_question_answer_from_schema(
            card_schema, deck["cards"][card_id]
        )

        question = Template(question_template).render(**deck["cards"][card_id])
        answer = Template(answer_template).render(**deck["cards"][card_id])
        return card_id, card_type, question, answer

    def process_result(self, deck, card_id, card_type, result):
        card_data = deck["cards"][card_id]
        if result == "correct":
            card_data["reviews"][card_type] = (
                card_data["reviews"].get(card_type, 0) or 0
            ) + 1
        else:
            reviews = []
            for card_data in deck["cards"].values():
                reviews += [review for review in card_data.get("reviews", {}).values() if review is not None]
            card_data["reviews"][card_type] = max(min(reviews or []) - 1, 0)



ALGORITHMS: Dict[str, Algorithm] = {
    "Random": Random(),
    "HardestFirst": HardestFirst(),
}
