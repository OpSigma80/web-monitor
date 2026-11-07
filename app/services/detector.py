"""
Lógica de detección de cambios y generación de resúmenes legibles.
"""

from typing import Optional
import re


def normalize_text(value: str) -> str:
    if not value:
        return ""
    text = value.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_number(value: str) -> Optional[float]:
    if not value:
        return None
    cleaned = re.sub(r"[^\d,.-]", "", value)
    cleaned = cleaned.replace(".", "").replace(",", ".") if "," in cleaned and "." in cleaned else cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def has_significant_change(
    old_value: Optional[str],
    new_value: str,
    threshold_percent: Optional[float] = None,
) -> bool:
    old_norm = normalize_text(old_value) if old_value else ""
    new_norm = normalize_text(new_value)

    if old_norm == new_norm:
        return False

    if threshold_percent is not None:
        old_num = extract_number(old_norm)
        new_num = extract_number(new_norm)
        if old_num is not None and new_num is not None and old_num != 0:
            change_pct = abs((new_num - old_num) / old_num) * 100
            return change_pct >= threshold_percent

    return True


def build_summary(
    monitor_name: str,
    old_value: Optional[str],
    new_value: str,
    monitor_type: str = "selector",
) -> str:
    old_norm = normalize_text(old_value) if old_value else "(sin valor previo)"
    new_norm = normalize_text(new_value)

    old_num = extract_number(old_norm)
    new_num = extract_number(new_norm)

    if old_num is not None and new_num is not None and old_num != 0:
        diff = new_num - old_num
        pct = (diff / old_num) * 100
        direction = "subió" if diff > 0 else "bajó"
        return (
            f"[{monitor_name}] El valor {direction} de {old_norm} a {new_norm} "
            f"({diff:+.2f} / {pct:+.1f}%)"
        )

    return f"[{monitor_name}] Cambió de «{old_norm}» a «{new_norm}»"