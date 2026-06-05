def normalize(value, min_value, max_value):
    if max_value == min_value:
        return 0
    return (value - min_value) / (max_value - min_value)


def check_deadline_violation(option, workload):
    finish_time = option["hours_from_now"] + workload["duration_hours"]
    return finish_time > workload["deadline_hours"]


def score_option(option, workload):
    carbon_score = normalize(option["carbon_intensity"], 200, 600)
    grid_score = normalize(option["grid_load"], 40, 100)
    latency_score = normalize(option["latency_score"], 0, 100)

    deadline_violation = check_deadline_violation(option, workload)

    if deadline_violation:
        deadline_score = 1.0
    elif workload["delay_tolerant"]:
        deadline_score = 0.2
    else:
        deadline_score = 0.6

    total_score = (
        0.40 * carbon_score
        + 0.30 * grid_score
        + 0.20 * deadline_score
        + 0.10 * latency_score
    )

    # Strong penalty for deadline violation
    if deadline_violation:
        total_score += 1.0

    approval_required = (
        option["grid_load"] >= 85
        or not workload["delay_tolerant"]
        or deadline_violation
        or total_score >= 0.65
    )

    return round(total_score, 3), approval_required, deadline_violation


def recommend_schedule(workload, options):
    ranked = []

    for option in options:
        score, approval_required, deadline_violation = score_option(option, workload)

        finish_time = option["hours_from_now"] + workload["duration_hours"]

        ranked.append({
            **option,
            "finish_within_hours": finish_time,
            "deadline_violation": deadline_violation,
            "score": score,
            "approval_required": approval_required
        })

    # Prefer non-deadline-violating options first, then lowest score
    ranked = sorted(ranked, key=lambda x: (x["deadline_violation"], x["score"]))
    best = ranked[0]

    lowest_carbon_option = min(options, key=lambda x: x["carbon_intensity"])

    selected_emissions = workload["energy_kwh"] * best["carbon_intensity"] / 1000
    lowest_carbon_emissions = workload["energy_kwh"] * lowest_carbon_option["carbon_intensity"] / 1000

    carbon_delta_vs_lowest = selected_emissions - lowest_carbon_emissions

    grid_stress_avoided = (
        lowest_carbon_option["grid_load"] >= 85
        and best["grid_load"] < 85
    )

    return {
        "workload": workload,
        "best_option": best,
        "all_options": ranked,
        "lowest_carbon_option": lowest_carbon_option,
        "selected_emissions_kg": round(selected_emissions, 2),
        "lowest_carbon_emissions_kg": round(lowest_carbon_emissions, 2),
        "carbon_delta_vs_lowest_kg": round(carbon_delta_vs_lowest, 2),
        "grid_stress_avoided": grid_stress_avoided,
    }