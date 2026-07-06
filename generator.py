"""
Phishing Simulation Content Generator
--------------------------------------
Generates TEMPLATED, LOCAL-ONLY phishing email *simulations* for security
awareness training -- no real sending, no external APIs, no live domains
contacted. Mirrors the kind of AI-driven simulation content a cybersecurity
training platform (e.g. revel8) would need to produce for its "human
firewall" training exercises.

Each generated email is then scored by a rule-based "red flag" detector
that estimates how realistic/detectable the email is, for calibrating
simulation difficulty (e.g. "easy" decoys with obvious red flags for
beginner training tracks vs. "hard" decoys with few flags for advanced
tracks).
"""

import itertools
import json
import random

random.seed(42)  # reproducible output

# ---------------------------------------------------------------------------
# 1. Template components (all fictional; no real companies/domains used)
# ---------------------------------------------------------------------------

PRETEXTS = [
    {
        "subject": "Action Required: Verify Your Account Access",
        "body": "We noticed unusual sign-in activity on your account. To keep your "
                "account secure, please verify your identity immediately.",
        "urgency": "immediately",
    },
    {
        "subject": "Invoice Payment Overdue",
        "body": "Your recent invoice payment has failed to process. Please update "
                "your payment details before your service is suspended.",
        "urgency": "before your service is suspended",
    },
    {
        "subject": "IT Password Reset Required",
        "body": "Our records show your password will expire today. Reset it now "
                "to avoid being locked out of your account.",
        "urgency": "today",
    },
]

SENDER_NAMES = ["IT Support Team", "Account Security", "Billing Department", "Contoso Corp"]

# Mostly spoofed domains, but ONE legitimate-looking option is included so the
# scorer has real variance to detect (see README debug note).
SENDER_DOMAINS = ["secure-verify-portal.net", "account-alerts-service.com",
                  "billing-notice-team.org", "contoso.com"]
CLAIMED_COMPANY = "Contoso Corp"  # fictional placeholder company

GREETINGS = ["Dear Customer,", "Dear User,", "Hello,", "Dear Alex Meier,"]

LINK_TEXTS = ["Verify Account", "Update Payment Info", "Reset Password Now"]
LINK_DOMAINS = ["contoso-secure-login.net", "contoso.account-verify.com",
                "verify-contoso-portal.info", "contoso.com"]

URGENCY_PHRASES = ["immediately", "within 24 hours", "before your account is suspended", "today"]


# ---------------------------------------------------------------------------
# 2. Generator
# ---------------------------------------------------------------------------

def generate_email(pretext, sender_name, sender_domain, greeting, link_text, link_domain):
    from_line = f'"{sender_name}" <no-reply@{sender_domain}>'
    body = (
        f"{greeting}\n\n"
        f"{pretext['body']}\n\n"
        f"Please act {random.choice(URGENCY_PHRASES)}: [{link_text}](https://{link_domain}/login)\n\n"
        f"Thank you,\n{sender_name}"
    )
    return {
        "from": from_line,
        "subject": pretext["subject"],
        "greeting": greeting,
        "body": body,
        "link_text": link_text,
        "link_domain": link_domain,
        "claimed_company": CLAIMED_COMPANY,
    }


def generate_variants(n=6):
    combos = list(itertools.product(
        PRETEXTS, SENDER_NAMES, SENDER_DOMAINS, GREETINGS, LINK_TEXTS, LINK_DOMAINS
    ))
    random.shuffle(combos)
    variants = []
    for combo in combos[:n]:
        variants.append(generate_email(*combo))
    return variants


# ---------------------------------------------------------------------------
# 3. Rule-based red flag scorer
# ---------------------------------------------------------------------------

RED_FLAG_RULES = [
    ("generic_greeting", lambda e: e["greeting"] in ("Dear Customer,", "Dear User,", "Hello,")),
    ("urgency_language", lambda e: any(p in e["body"].lower() for p in
        ["immediately", "within 24 hours", "suspended", "today", "act now"])),
    ("sender_domain_not_company_domain", lambda e: e["from"].split("@")[-1].rstrip(">") != "contoso.com"),
    ("suspicious_link_domain", lambda e: e["link_domain"] != "contoso.com"),
    ("generic_role_display_name", lambda e: any(w in e["from"].lower() for w in
        ["support", "security", "billing"])),
    ("request_via_embedded_link", lambda e: "[" in e["body"] and "](" in e["body"]),
]


def score_email(email):
    """
    NOTE (debugging finding): the first version of this scorer used
    "contoso.com" as the only whitelisted domain, but the generator's
    component lists never actually produced "contoso.com" as an option --
    so every generated email hit all 6 rules and realism_score was always 0
    with no variance. Fixed by adding a genuinely clean option to
    SENDER_DOMAINS, LINK_DOMAINS, and GREETINGS so the scorer has real
    variance to detect. Also corrected an inverted difficulty mapping:
    more flags detected means the email is MORE obviously fake, i.e.
    EASIER for a trainee to spot, not harder.
    """
    flags = []
    for name, rule in RED_FLAG_RULES:
        try:
            if rule(email):
                flags.append(name)
        except Exception:
            pass
    total = len(RED_FLAG_RULES)
    hit = len(flags)
    realism_score = round(100 * (1 - hit / total))  # fewer flags -> more realistic/harder to spot
    if hit >= 5:
        difficulty = "easy (many obvious flags -- good for beginner training)"
    elif hit >= 2:
        difficulty = "medium"
    else:
        difficulty = "hard (few flags -- good for advanced training)"
    return {
        "flags_detected": flags,
        "flag_count": hit,
        "total_rules_checked": total,
        "realism_score": realism_score,
        "suggested_difficulty_tier": difficulty,
    }


# ---------------------------------------------------------------------------
# 4. Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    variants = generate_variants(n=6)
    report = []
    for i, email in enumerate(variants, start=1):
        scoring = score_email(email)
        report.append({"variant": i, "email": email, "scoring": scoring})

    with open("generated_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
