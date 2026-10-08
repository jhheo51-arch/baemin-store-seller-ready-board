"""Deterministic reconstruction of the original synthetic queue model.
Input: published work_tasks.csv; no network or customer data.
"""
import math
import pandas as pd

POLICIES = ("접수 순서", "오래 대기, 재문의 우선", "판매 준비 임박 우선")
REQUIRED = {"task_id", "release_day", "effort_hours", "repeat_contact_count", "severity", "progress_stage"}

def validate_inputs(tasks, policy, days, capacity):
    if policy not in POLICIES:
        raise ValueError("Unknown policy")
    if not isinstance(days, int) or days <= 0 or not math.isfinite(capacity) or capacity < 0:
        raise ValueError("Invalid horizon or capacity")
    if not REQUIRED.issubset(tasks.columns):
        raise ValueError("Required task columns are missing")
    if tasks.task_id.isna().any() or tasks.task_id.duplicated().any():
        raise ValueError("Task identifiers must be present and unique")
    for column in REQUIRED - {"task_id"}:
        values = pd.to_numeric(tasks[column], errors="coerce")
        if values.isna().any() or not values.map(math.isfinite).all() or (values < 0).any():
            raise ValueError("Invalid numeric task value: " + column)
    if ((tasks.release_day % 1 != 0) | (tasks.release_day >= days)).any() or (tasks.effort_hours <= 0).any():
        raise ValueError("Tasks must arrive within the horizon and require positive effort")

def empty_result(policy):
    return dict(policy=policy, completed_tasks=0, unresolved_tasks=0,
                completion_rate=None, median_wait_days=None, p90_wait_days=None,
                sla_3day_rate=None, ready_stage_sla_3day_rate=None,
                max_wait_unresolved_days=0)

def percentile(series: pd.Series, q: float) -> float:
    clean = series.dropna()
    return round(float(clean.quantile(q)), 1) if len(clean) else None


def simulate_policy(tasks: pd.DataFrame, policy: str, days: int = 56, capacity_per_day: float = 80.0):
    validate_inputs(tasks, policy, days, capacity_per_day)
    if tasks.empty:
        return empty_result(policy)
    queue = []
    completed = []
    for day in range(days):
        arrivals = tasks[tasks.release_day == day].to_dict("records")
        queue.extend(arrivals)
        if policy == "접수 순서":
            queue.sort(key=lambda x: (x["release_day"], x["task_id"]))
        elif policy == "오래 대기, 재문의 우선":
            queue.sort(
                key=lambda x: (
                    -((day - x["release_day"]) + 2.5 * x["repeat_contact_count"] + 2 * x["severity"]),
                    x["release_day"],
                )
            )
        elif policy == "판매 준비 임박 우선":
            queue.sort(
                key=lambda x: (
                    -x["progress_stage"],
                    -(day - x["release_day"]),
                    -x["repeat_contact_count"],
                )
            )
        capacity = capacity_per_day
        remaining = []
        for task in queue:
            if task["effort_hours"] <= capacity:
                capacity -= task["effort_hours"]
                task = dict(task)
                task["completed_day"] = day
                task["wait_days"] = max(0, day - task["release_day"])
                completed.append(task)
            else:
                remaining.append(task)
        queue = remaining
    completed_df = pd.DataFrame(completed, columns=[*tasks.columns, "completed_day", "wait_days"])
    ready_tasks = completed_df[completed_df.progress_stage >= 4] if len(completed_df) else completed_df
    return {
        "policy": policy,
        "completed_tasks": int(len(completed_df)),
        "unresolved_tasks": int(len(queue)),
        "completion_rate": round(len(completed_df) / len(tasks), 3),
        "median_wait_days": percentile(completed_df.wait_days, 0.5),
        "p90_wait_days": percentile(completed_df.wait_days, 0.9),
        "sla_3day_rate": round(float((completed_df.wait_days <= 3).mean()), 3) if len(completed_df) else None,
        "ready_stage_sla_3day_rate": round(float((ready_tasks.wait_days <= 3).mean()), 3) if len(ready_tasks) else None,
        "max_wait_unresolved_days": int(max([days - 1 - task["release_day"] for task in queue], default=0)),
    }


