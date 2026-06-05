workloads = [
    {
        "job": "AI batch inference",
        "duration_hours": 2,
        "deadline_hours": 8,
        "delay_tolerant": True,
        "energy_kwh": 120,
    },
    {
        "job": "Critical database backup",
        "duration_hours": 1,
        "deadline_hours": 2,
        "delay_tolerant": False,
        "energy_kwh": 80,
    },
    {
        "job": "ETL analytics pipeline",
        "duration_hours": 3,
        "deadline_hours": 10,
        "delay_tolerant": True,
        "energy_kwh": 150,
    },
    {
    "job": "Urgent AI model retraining",
    "duration_hours": 4,
    "deadline_hours": 6,
    "delay_tolerant": False,
    "energy_kwh": 300,
    },

]


schedule_options = [
    {
        "region": "Region A",
        "hour": "10:00",
        "hours_from_now": 1,
        "carbon_intensity": 220,
        "grid_load": 94,
        "latency_score": 30,
    },
    {
        "region": "Region B",
        "hour": "14:00",
        "hours_from_now": 3,
        "carbon_intensity": 330,
        "grid_load": 58,
        "latency_score": 35,
    },
    {
        "region": "Region C",
        "hour": "18:00",
        "hours_from_now": 7,
        "carbon_intensity": 500,
        "grid_load": 60,
        "latency_score": 20,
    },
    {
        "region": "Region D",
        "hour": "22:00",
        "hours_from_now": 11,
        "carbon_intensity": 360,
        "grid_load": 45,
        "latency_score": 40,
    },
]