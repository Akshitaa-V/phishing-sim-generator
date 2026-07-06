# Phishing Simulation Content Generator

A local, offline Python tool that generates **templated phishing email
simulations** for security-awareness training, plus a rule-based **red flag
scorer** that estimates how realistic/detectable each generated email is —
useful for calibrating training difficulty tiers (beginner vs. advanced).

**No real emails are sent. No external APIs, accounts, or live domains are
contacted.** All company names and domains used are fictional placeholders
("Contoso Corp"). This mirrors the type of AI-generated attack-simulation
content a cybersecurity training platform needs to produce for its exercises.

## How it works
1. `generate_variants()` combines pretext templates (account-verification,
   invoice-overdue, password-reset), sender display names, sender domains,
   greetings, and link text/domains to produce distinct email variants.
2. `score_email()` checks each generated email against 6 rule-based red
   flags: generic greeting, urgency language, sender-domain mismatch,
   suspicious link domain, generic role-based display name, and
   request-via-embedded-link.
3. Each email gets a `realism_score` (0–100, higher = more realistic / fewer
   flags) and a suggested difficulty tier (easy / medium / hard) for
   training use.

## Debugging note (real issue found while building this)
The first version of the scorer whitelisted `contoso.com` as the only
"clean" sender/link domain, but the generator's own template component
lists never actually included `contoso.com` as an option — so **every**
generated email tripped all 6 rules and `realism_score` was always 0, with
zero variance between variants. Fixed by adding a genuinely clean domain,
greeting, and sender-name option into the generator's component lists so
the scorer has real signal to differentiate on. Also caught and fixed an
inverted difficulty-tier mapping that had labeled high-flag-count (i.e.
obviously fake) emails as "hard" instead of "easy."

## Results (this run, 6 generated variants)
- Flag count range across variants: **3–6 out of 6 rules**
- Difficulty tier distribution: **5 easy, 1 medium** (no all-clean "hard"
  variant appeared in this random sample of 6 — expected, since most
  template combinations still include at least one spoofed domain)
- The one "medium" variant used the legitimate sender domain
  (`contoso.com`) but still tripped urgency-language and embedded-link
  rules, showing the scorer catches partial realism correctly.

## Files
- `generator.py` — template components, generator, red-flag scorer, run script
- `generated_report.json` — full generated output from this run (6 variants
  with scoring)

## Run it yourself
```bash
python3 generator.py
```
No dependencies beyond the Python standard library.
