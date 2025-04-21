import re
import logging
from bias_detector import detect_bias

logger = logging.getLogger(__name__)

BIAS_PATTERNS = [
    r'\b(women are (naturally|better|worse|too emotional|not (technical|logical|strong|capable)))\b',
    r'\b(men are (naturally|better|worse|too (aggressive|logical|technical|unemotional)))\b',
    r'\b(woman\'s place|men\'s work|girls can\'t|boys don\'t|female-friendly|male-dominated)\b',
    r'\b(women|females|girls) (can\'t|cannot|don\'t|do not|aren\'t able to|are not capable of) (do|handle|manage|work|perform|excel at|lead|code|program|engineer|run)\b',
    r'\b(women|females) (aren\'t|are not) (good|suitable|qualified|smart enough|strong enough|capable enough|fit) for (jobs|work|careers|leadership|management|tech|science|math)\b',
    r'\b(women|females|girls) .{0,20}(can\'t|cannot|shouldn\'t|should not) .{0,20}(job|work|career|profession|position|company|business|lead|manage)\b',
    r'\b(manpower|mankind|man-made|chairman|policeman|fireman|stewardess|mailman|congressman)\b',
    r'\b(girls|ladies) when referring to (professional|adult) women\b',
    r'\bshe (should|needs to) (smile more|be friendlier|be more pleasant|be less aggressive)\b',
    r'\b(maternal|caring|nurturing) (qualities|instincts|nature) for women\b',
    r'\b(technical|analytical|logical) (positions|roles|jobs) for men\b',
    r'\b(assertive women|bossy|shrill|hysterical|emotional|catty|bitchy)\b',
    r'\b(working mother|career woman) but not (working father|career man)\b',
    r'\b(female doctor|woman engineer|lady lawyer) but not (male doctor|man engineer)\b',

    r'\b(too old|too young) for (this job|this position|this role|this field|this industry)\b',
    r'\b(young blood|old guard|digital natives|boomers|millennials|gen z|gen x)\b',
    r'\b(over the hill|old school|dinosaur|past prime|set in ways)\b',
    r'\b(inexperienced|naive|entitled|lazy) generation\b',
    r'\b(retirement age|aging workforce|aging out)\b',

    r'\b(minorities are|immigrants are|people from|foreigners are|ethnic people)\b',
    r'\b(cultural fit|speak like a native|heavy accent|foreign accent)\b',
    r'\b(articulate|well-spoken) for (a|an) (minority|person of color)\b',
    r'\b(diverse candidate|diversity hire|token)\b',
    r'\b(model minority|urban|inner city|ghetto|exotic|Oriental)\b',

    r'\b(looks professional|appears professional|dress code|attractive|presentable)\b',
    r'\b(unprofessional hair|unprofessional appearance|dress more appropriately)\b',
    r'\b(weight|size|height|beauty|pretty|handsome) (requirement|qualification|asset)\b',
    r'\b(face for|looks for|appearance for) (customer service|front desk|reception|sales)\b',

    r'\b(childcare|maternity|paternity|family commitments|work-life|married|single)\b',
    r'\b(planning (on having|to have) children|pregnancy plans|family plans)\b',
    r'\b(primary caregiver|single parent|married with children)\b',

    r'\b(handicapped|special needs|differently abled|disabled person)\b',
    r'\b(suffers from|afflicted with|victim of) (disability|condition)\b',
    r'\b(wheelchair-bound|confined to wheelchair|normal people|healthy people)\b',
    r'\b(mentally ill|mentally challenged|slow|retarded|crippled)\b',

    r'\b(lifestyle choice|preference|alternative lifestyle|normal sexuality)\b',
    r'\b(real man|real woman|feminine enough|masculine enough|girly|effeminate)\b',

    r'\b(poor people are|low income people|people on welfare|lower class)\b',
    r'\b(elite school|prestigious background|right family|right neighborhood)\b',
]

OFF_TOPIC_PATTERNS = [
    r'\b(joke|funny|humor|weather|sports|politics|religion|news)\b',
    r'\b(tell me about yourself|who are you|are you real|are you ai|who made you)\b',
    r'\b(sing|dance|play|game|movie|music|book|recommend)\b',
    r'\b(buy|purchase|shop|shopping|product|store|headphone|electronics|clothes|shoes)\b',
    r'\b(price|cost|cheap|expensive|discount|sale|deal|offer)\b',
]

PERSONAL_QUESTION_PATTERNS = [
    r'\b(your opinion|what do you think about|do you believe|what is your take)\b',
    r'\b(your favorite|you prefer|you like|you enjoy|you hate|you dislike)\b',
    r'\b(tell me about you|about yourself|your creator|who made you)\b',
]


def check_and_handle_bias(user_message):
    lower_message = user_message.lower()

    for pattern in BIAS_PATTERNS:
        if re.search(pattern, lower_message):
            logger.info(f"Bias detected in message: {user_message}")

            response_options = [
                "I appreciate your question! 🌸 At JobsForHer, we believe in inclusive and equitable language that empowers everyone. Could we reframe your question to use more inclusive terms? I'm here to help you find the right resources for your career journey.",

                "Thank you for reaching out. 🌷 I noticed some wording in your question that we could make more inclusive. JobsForHer is all about empowering careers without limitations. Would you mind rephrasing your question? I'm excited to help you with your career growth!",

                "Your career growth matters to me! 🌺 I noticed some language that might unintentionally reinforce stereotypes. Could we rephrase your question with more inclusive terminology? I'd love to provide you with helpful information on jobs, events, and mentorship opportunities.",

                "Let's grow together! 🌹 To ensure we're creating an inclusive environment for all professionals, could we reframe your question with more neutral wording? I'm here to support your career journey with helpful resources and opportunities.",

                "I'm so glad you're here! 🌻 At JobsForHer, we value inclusive language that breaks down barriers rather than reinforcing them. Could we rephrase your question to be more inclusive? I'm eager to help you find the perfect resources for your professional growth!"
            ]

            import random
            return random.choice(response_options)

    return None


def check_for_off_topic(user_message):
    lower_message = user_message.lower()

    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, lower_message):
            logger.info(f"Off-topic query detected: {user_message}")

            response_options = [
                "I appreciate your query! 🌸 However, I'm Asha, a career counselor at JobsForHer Foundation, focused on helping women with their professional growth. I can't assist with shopping or product recommendations, but I'd be happy to help you explore job opportunities, career events, or mentorship programs. How can I support your career journey?",

                "Thanks for reaching out! 🌺 Just to clarify - I'm Asha, a career counselor specialized in helping women advance their careers. While I can't help with purchasing products, I'd love to assist you with job searches, professional development, or finding a mentor. What career-related support are you looking for?",

                "Hello! 🍪 I'm Asha, your dedicated career counselor at JobsForHer. While I can't help with shopping or product recommendations, my expertise lies in career guidance, job opportunities, and professional development. Would you like to explore any of these areas?",

                "Thanks for your message! 🌼 I'm Asha, and I specialize in career support for the JobsForHer community. I'd be delighted to help you find job opportunities, upcoming events, mentorship programs, or professional development resources. What aspect of your career would you like to explore?",

                "Sending you a virtual cookie! 🍪 I'm Asha, your career growth companion at JobsForHer. While I can't help with that specific topic, I'd be thrilled to assist you with finding job opportunities, career events, mentorship connections, or professional development resources. How can I support your career journey today?",

                "Hi there! 🌷 I'm Asha from JobsForHer. While that's not my area of expertise, I'd be happy to help you discover exciting job opportunities, connect you with mentors, find career-building events, or explore professional development resources. What are you looking to achieve in your career?",

                "Warm greetings! 🌺 I'm Asha, your dedicated career assistant. I specialize in helping with career-related information like job opportunities, professional events, mentorship programs, and skill development resources. I'd love to help you take your next career step - what are you interested in exploring?"
            ]

            import random
            return random.choice(response_options)

    return None


def check_for_personal_questions(user_message):
    lower_message = user_message.lower()

    for pattern in PERSONAL_QUESTION_PATTERNS:
        if re.search(pattern, lower_message):
            logger.info(f"Personal question detected: {user_message}")

            response_options = [
                "I appreciate your curiosity! 🌸 While I don't have personal preferences, I'd love to focus on helping you with factual information about career opportunities through JobsForHer. What kind of career information would be most helpful for your journey right now?",

                "Thanks for asking! 🍪 As your career assistant, I'm here to provide objective information rather than personal opinions. I'd be delighted to help you explore job opportunities, career events, or mentorship programs that match your interests. What would you like to know about?",

                "What a thoughtful question! 🌷 Rather than sharing personal views, I'd love to help you with factual information about the amazing opportunities at JobsForHer. Would you like to explore job listings, upcoming events, or mentorship programs tailored to your career goals?",

                "I appreciate your interest! 🌺 While I don't have personal opinions, I'm passionate about helping you with your career journey. I can share information about job opportunities, professional events, mentorship programs, and career resources. How can I support your growth today?",

                "That's an interesting question! 🌹 I'm focused on being your helpful career companion by providing factual information rather than personal views. I'd be thrilled to help you discover career opportunities, events, or mentorship programs through JobsForHer. What are you most interested in exploring?"
            ]

            import random
            return random.choice(response_options)

    return None


def check_for_sensitive_topics(user_message):
    sensitive_patterns = [
        r'\b(salary negotiation|pay gap|discrimination|harassment|toxic workplace)\b',
        r'\b(mental health|depression|anxiety|stress|burnout)\b',
        r'\b(lawsuit|legal action|sue|complaint|grievance)\b'
    ]

    lower_message = user_message.lower()

    for pattern in sensitive_patterns:
        if re.search(pattern, lower_message):
            logger.info(f"Sensitive topic detected: {user_message}")

            response_options = [
                "Thank you for bringing up this important topic. 🌸 Your wellbeing matters! For sensitive workplace matters like this, connecting with a mentor who can provide personalized guidance might be most helpful. JobsForHer offers wonderful mentorship programs - would you like me to share information about these opportunities?",

                "I appreciate you trusting me with this topic. 🌷 This deserves thoughtful, personalized guidance from someone who can fully understand your specific situation. JobsForHer connects women with experienced mentors who can provide this kind of support. Would you like to learn more about these mentorship opportunities?",

                "This is certainly an important matter. 🌺 While I can offer general information, I believe you deserve specialized support for this topic. JobsForHer has a network of experienced mentors who can provide the nuanced guidance you deserve. Would you like me to share details about connecting with a mentor?",

                "Your question touches on something significant. 🌹 For matters like this, speaking with a career mentor who can understand your unique circumstances would be most valuable. JobsForHer offers mentorship programs designed to provide this personalized support. Would you like information about these programs?",

                "I care about your wellbeing! 🍪 For sensitive workplace matters, having a conversation with a mentor who can provide tailored guidance based on your specific situation would be most beneficial. JobsForHer connects women with experienced professionals through our mentorship programs. Would you like to learn more about these opportunities?"
            ]

            import random
            return random.choice(response_options)

    return None


def check_for_hallucination_risk(user_message):
    hallucination_patterns = [
        r'\b(predict|forecast|future|trend|outlook|projection)\b',
        r'\b(will i|can i|should i|would i|could i)\b',
        r'\b(guarantee|promise|ensure|certain|definitely)\b'
    ]

    lower_message = user_message.lower()

    for pattern in hallucination_patterns:
        if re.search(pattern, lower_message):
            logger.info(f"Potential hallucination risk detected: {user_message}")

            response_options = [
                "I'd love to help you make an informed decision! 🌸 While I can't predict the future, I can provide factual information about current opportunities at JobsForHer. Would you like to explore available job listings, upcoming events, or mentorship programs that might help you chart your own path forward?",

                "Great question! 🍪 I focus on providing reliable, current information rather than predictions. I'd be happy to share details about existing job opportunities, scheduled events, or established mentorship programs that could help you make your own well-informed decision. What specific information would be most helpful?",

                "That's an excellent consideration! 🌷 Rather than making predictions, I can offer you factual information about current opportunities through JobsForHer. Would you like to explore available jobs, upcoming events, or mentorship programs that align with your interests? These resources might help you form your own perspective.",

                "I appreciate your forward-thinking question! 🌺 While I can't predict outcomes, I'd be delighted to share current information about job opportunities, career events, and mentorship programs at JobsForHer. This factual information might help you make your own decision. What specific area interests you most?",

                "I'm excited to help you explore possibilities! 🌹 Instead of predictions, I can provide you with current, factual information about opportunities at JobsForHer. Would you like to learn about available job listings, upcoming events, or established mentorship programs? This information might help you chart your own career path."
            ]

            import random
            return random.choice(response_options)

    return None


def check_ml_bias(user_message):
    is_biased, bias_score, explanation = detect_bias(user_message)
    if is_biased:
        logger.info(f"ML-detected bias in message: {user_message} (score: {bias_score})")
        return explanation
    return None


def apply_all_guardrails(user_message):
    checks = [
        check_ml_bias,
        check_and_handle_bias,
        check_for_off_topic,
        check_for_personal_questions,
        check_for_sensitive_topics,
        check_for_hallucination_risk
    ]

    for check_function in checks:
        result = check_function(user_message)
        if result:
            return result

    return None#