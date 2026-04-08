from SysGuard.config import (
    HIGH_RISK_THRESHOLD,
    IGNORED_PATH_PATTERNS,
    MEDIUM_RISK_THRESHOLD,
    RISK_SCORES,
)


def should_ignore_event(event):
    target = event.get("target", "")
    return any(pattern in target for pattern in IGNORED_PATH_PATTERNS)


def calculate_risk(events):
    score = 0

    for event in events:
        if event.get("suppressed"):
            continue
        if should_ignore_event(event):
            continue
        event_type = event.get("type")
        if not event_type:
            continue
        score += RISK_SCORES.get(event_type, 0)

    if score >= HIGH_RISK_THRESHOLD:
        level = "HIGH"
    elif score >= MEDIUM_RISK_THRESHOLD:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": score,
        "level": level
    }
