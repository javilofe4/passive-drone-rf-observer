from ..models import Alert


def evaluate_alert(aggregated_prob: float) -> Alert:
    if aggregated_prob < 0.2:
        level = "none"
    elif aggregated_prob < 0.5:
        level = "low"
    elif aggregated_prob < 0.75:
        level = "medium"
    else:
        level = "high"

    message = f"Aggregated drone-like probability: {aggregated_prob:.2f}"
    return Alert(level=level, probability=aggregated_prob, message=message)
