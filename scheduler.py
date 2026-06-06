from policy import (
    CARBON_WEIGHT,
    GRID_WEIGHT,
    DEADLINE_WEIGHT,
    LATENCY_WEIGHT,
    GRID_STRESS_THRESHOLD,
    MODERATE_GRID_THRESHOLD,
    HIGH_RISK_SCORE_THRESHOLD,
    CARBON_MIN,
    CARBON_MAX,
    GRID_MIN,
    GRID_MAX,
    LATENCY_MIN,
    LATENCY_MAX,
)


def normalize(value, min_value, max_value):
    if max_value == min_value:
        return 0
    return max(0, min(1, (value - min_value) / (max_value - min_value)))


def score_option(option, workload):
    finish_within_hours = option["hours_from_now"] + workload["duration_hours"]
    deadline_violation = finish_within_hours > workload["deadline_hours"]

    carbon_score = normalize(option["carbon_intensity"], CARBON_MIN, CARBON_MAX)
    grid_score = normalize(option["grid_load"], GRID_MIN, GRID_MAX)
    latency_score = normalize(option["latency_score"], LATENCY_MIN, LATENCY_MAX)

    if deadline_violation:
        deadline_score = 1.0
    elif workload["delay_tolerant"]:
        deadline_score = 0.2
    else:
        deadline_score = 0.6

    carbon_component = CARBON_WEIGHT * carbon_score
    grid_component = GRID_WEIGHT * grid_score
    deadline_component = DEADLINE_WEIGHT * deadline_score
    latency_component = LATENCY_WEIGHT * latency_score

    total_score = (
        carbon_component
        + grid_component
        + deadline_component
        + latency_component
    )

    reason_codes = []

    if option["grid_load"] >= GRID_STRESS_THRESHOLD:
        reason_codes.append("HIGH_GRID_STRESS")

    if option["grid_load"] >= MODERATE_GRID_THRESHOLD:
        reason_codes.append("MODERATE_OR_HIGH_GRID_LOAD")

    if deadline_violation:
        reason_codes.append("DEADLINE_VIOLATION")
    else:
        reason_codes.append("DEADLINE_FEASIBLE")

    if not workload["delay_tolerant"]:
        reason_codes.append("NON_DELAY_TOLERANT_WORKLOAD")

    approval_required = (
        option["grid_load"] >= GRID_STRESS_THRESHOLD
        or deadline_violation
        or total_score >= HIGH_RISK_SCORE_THRESHOLD
        or (
            not workload["delay_tolerant"]
            and option["grid_load"] >= MODERATE_GRID_THRESHOLD
        )
    )

    if approval_required:
        reason_codes.append("HUMAN_APPROVAL_REQUIRED")
    else:
        reason_codes.append("AUTO_APPROVED_LOW_RISK")

    score_breakdown = {
        "carbon_component": round(carbon_component, 3),
        "grid_component": round(grid_component, 3),
        "deadline_component": round(deadline_component, 3),
        "latency_component": round(latency_component, 3),
    }

    return {
        "score": round(total_score, 3),
        "approval_required": approval_required,
        "deadline_violation": deadline_violation,
        "finish_within_hours": finish_within_hours,
        "score_breakdown": score_breakdown,
        "reason_codes": reason_codes,
    }


def recommend_schedule(workload, options):
    ranked = []

    for option in options:
        scoring = score_option(option, workload)

        ranked.append({
            **option,
            "finish_within_hours": scoring["finish_within_hours"],
            "deadline_violation": scoring["deadline_violation"],
            "score": scoring["score"],
            "approval_required": scoring["approval_required"],
            "score_breakdown": scoring["score_breakdown"],
            "reason_codes": scoring["reason_codes"],
        })

    feasible_options = [o for o in ranked if not o["deadline_violation"]]

    if feasible_options:
        if workload["delay_tolerant"]:
            grid_safe_feasible_options = [
                o for o in feasible_options
                if o["grid_load"] < GRID_STRESS_THRESHOLD
            ]

            if grid_safe_feasible_options:
                best = sorted(grid_safe_feasible_options, key=lambda x: x["score"])[0]
            else:
                best = sorted(feasible_options, key=lambda x: x["score"])[0]
        else:
            best = sorted(feasible_options, key=lambda x: x["score"])[0]
    else:
        best = sorted(ranked, key=lambda x: x["score"])[0]

    ranked = sorted(
        ranked,
        key=lambda x: (x["deadline_violation"], x["score"])
    )

    lowest_carbon_option = min(options, key=lambda x: x["carbon_intensity"])

    selected_emissions = workload["energy_kwh"] * best["carbon_intensity"] / 1000
    lowest_carbon_emissions = (
        workload["energy_kwh"] * lowest_carbon_option["carbon_intensity"] / 1000
    )

    carbon_delta_vs_lowest = selected_emissions - lowest_carbon_emissions

    grid_stress_avoided = (
        lowest_carbon_option["grid_load"] >= GRID_STRESS_THRESHOLD
        and best["grid_load"] < GRID_STRESS_THRESHOLD
    )

    decision_reason_codes = list(best["reason_codes"])

    if (
        workload["delay_tolerant"]
        and lowest_carbon_option["grid_load"] >= GRID_STRESS_THRESHOLD
        and best["region"] != lowest_carbon_option["region"]
    ):
        decision_reason_codes.append(
            "FLEXIBLE_WORKLOAD_SHIFTED_AWAY_FROM_GRID_STRESS"
        )

    if grid_stress_avoided:
        decision_reason_codes.append("LOWEST_CARBON_REJECTED_GRID_STRESS")

    return {
        "workload": workload,
        "best_option": best,
        "all_options": ranked,
        "lowest_carbon_option": lowest_carbon_option,
        "selected_emissions_kg": round(selected_emissions, 2),
        "lowest_carbon_emissions_kg": round(lowest_carbon_emissions, 2),
        "carbon_delta_vs_lowest_kg": round(carbon_delta_vs_lowest, 2),
        "grid_stress_avoided": grid_stress_avoided,
        "decision_reason_codes": decision_reason_codes,
    }