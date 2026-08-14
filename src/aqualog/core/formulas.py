from __future__ import annotations

import math


def calculate_sar(*, na_meq_l: float, ca_meq_l: float, mg_meq_l: float) -> float:
    denominator_term = (ca_meq_l + mg_meq_l) / 2.0
    if denominator_term <= 0:
        raise ValueError("Ca + Mg must be greater than zero to calculate SAR.")
    return na_meq_l / math.sqrt(denominator_term)


def calculate_sodium_percentage(
    *, na_meq_l: float, k_meq_l: float, ca_meq_l: float, mg_meq_l: float
) -> float:
    total = na_meq_l + k_meq_l + ca_meq_l + mg_meq_l
    if total <= 0:
        raise ValueError("Total cations must be greater than zero.")
    return 100.0 * (na_meq_l + k_meq_l) / total


def calculate_total_hardness(*, ca_meq_l: float, mg_meq_l: float) -> float:
    if ca_meq_l < 0 or mg_meq_l < 0:
        raise ValueError("Ca and Mg cannot be negative.")
    return 50.0 * (ca_meq_l + mg_meq_l)


def calculate_ionic_balance(
    *,
    ca_meq_l: float,
    mg_meq_l: float,
    na_meq_l: float,
    k_meq_l: float,
    co3_meq_l: float,
    hco3_meq_l: float,
    cl_meq_l: float,
    so4_meq_l: float,
    no3_meq_l: float,
) -> float:
    cations = ca_meq_l + mg_meq_l + na_meq_l + k_meq_l
    anions = co3_meq_l + hco3_meq_l + cl_meq_l + so4_meq_l + no3_meq_l
    total = cations + anions
    if total <= 0:
        raise ValueError("Total ionic concentration must be greater than zero.")
    return 100.0 * (cations - anions) / total


def calculate_tds_ec_factor(*, tds_mg_l: float, ec_us_cm: float) -> float:
    if ec_us_cm <= 0:
        raise ValueError("EC must be greater than zero.")
    return tds_mg_l / ec_us_cm
