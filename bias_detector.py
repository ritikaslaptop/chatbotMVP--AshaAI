import logging
import re
import os

logger = logging.getLogger(__name__)

GENDER_BIASED_TERMS = [r'\b(women|females?) (can\'?t|cannot|shouldn\'?t|are not able to|don\'?t) (code|program|do math|be (engineers|leaders|CEOs|bosses)|do jobs)\b',
    r'\b(men|males?) (can\'?t|cannot|shouldn\'?t|are not able to|don\'?t) (nurture|care|be (nurses|assistants|secretaries))\b',

    r'\b(chairman|fireman|policeman|stewardess|waitress|salesgirl|cleaning lady)\b',

    r'\b(she|her) (should|needs to) (smile more|be nicer|be more agreeable|be less aggressive)\b',
    r'\b(he|him) (should|needs to) (be tough|not cry|be strong|hide emotions)\b',

    r'\b(women|females?) are (too emotional|less logical|weaker|less capable|less intelligent)\b',
    r'\b(men|males?) are (too aggressive|less caring|less nurturing|less emotional)\b',

    r'\bwomen can\'?t\b',
    r'\bfemales? can\'?t\b',
    r'\bwomen (don\'?t|cannot)\b',

    r'\ball (women|females?) are\b',
    r'\ball (men|males?) are\b',]

TOXICITY_PATTERNS = [r'\b(hate|despise|detest)\s+(women|men|girls|boys|females?|males?)\b',
    r'\b(stupid|dumb|idiotic|inferior|useless)\s+(women|men|girls|boys|females?|males?)\b',

    r'\bwomen\s+(belong|should stay|should be)\s+(at home|in the kitchen)\b',
    r'\bgender roles\b',
    r'\b(men|women) are better than (men|women)\b',

    r'\bwomen (aren\'t|are not|don\'t) (belong|fit|suitable) (in|at|for) (workplace|office|work|job)\b',
    r'\bmales? (only|exclusive|better suited)\b',
    r'\bfemales? (only|exclusive|better suited)\b',

    r'\b(all|most|typical) women (are|should|can\'t|must)\b',
    r'\b(all|most|typical) men (are|should|can\'t|must)\b',
    r'\bgirls (can\'t|don\'t|unable to) (handle|manage|perform|do|work|complete)\b',
    r'\bwomen jobs\b',
    r'\bmen jobs\b',]


def check_pattern_bias(text):
    for pattern in GENDER_BIASED_TERMS:
        if re.search(pattern, text.lower()):
            return "Your message contains a gender-biased statement that reinforces stereotypes. At JobsForHer, we believe in equal opportunities regardless of gender."

    for pattern in TOXICITY_PATTERNS:
        if re.search(pattern, text.lower()):
            return "Your message contains content that could be considered offensive or discriminatory. Please rephrase your request in a more respectful way."

    return None


def detect_bias(text):
    pattern_bias = check_pattern_bias(text)
    if pattern_bias:
        logger.info(f"Pattern-based bias detected in: '{text}'")
        return True, 0.9, pattern_bias
    return False, 0, "" #works