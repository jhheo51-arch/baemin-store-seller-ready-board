from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


SEED = 20261006
AS_OF = datetime(2026, 10, 6, 18, 0, 0)
WINDOW_START = datetime(2026, 8, 11, 9, 0, 0)
STAGES = ["신청", "서류 확인", "계약", "상품 등록", "판매 준비 완료"]
CATEGORIES = ["편의점", "마트", "뷰티", "패션", "꽃"]


def weighted_choice(rng: random.Random, values, weights):
    return rng.choices(values, weights=weights, k=1)[0]


def percentile(series: pd.Series, q: float) -> float:
    clean = series.dropna()
    return round(float(clean.quantile(q)), 1) if len(clean) else 0.0


def generate_sellers(rng: random.Random, count: int = 240) -> pd.DataFrame:
    rows = []
    for index in range(1, count + 1):
        applied_day = rng.randint(0, 55)
        applied_at = WINDOW_START + timedelta(days=applied_day, hours=rng.randint(0, 7))
        category = weighted_choice(rng, CATEGORIES, [30, 28, 18, 14, 10])
        product_count = max(5, round(rng.lognormvariate(2.85, 0.62)))
        digital_fluency = weighted_choice(rng, ["낮음", "보통", "높음"], [24, 52, 24])
        rows.append(
            {
                "seller_id": f"S{index:04d}",
                "category": category,
                "planned_products": product_count,
                "digital_fluency": digital_fluency,
                "applied_at": applied_at,
            }
        )
    return pd.DataFrame(rows).sort_values(["applied_at", "seller_id"]).reset_index(drop=True)


def generate_stage_history(rng: random.Random, sellers: pd.DataFrame) -> pd.DataFrame:
    stage_rules = {
        "서류 확인": (24, 2.2),
        "계약": (18, 1.4),
        "상품 등록": (42, 5.5),
        "판매 준비 완료": (20, 2.0),
    }
    rows = []
    for seller in sellers.itertuples(index=False):
        current = seller.applied_at
        reached_stage = "신청"
        rows.append(
            {
                "seller_id": seller.seller_id,
                "stage": "신청",
                "stage_order": 1,
                "started_at": seller.applied_at,
                "completed_at": seller.applied_at,
                "queue_hours": 0.0,
                "active_work_hours": 0.3,
                "rework_count": 0,
                "status": "완료",
            }
        )

        for order, stage in enumerate(STAGES[1:], start=2):
            base_wait, base_work = stage_rules[stage]
            fluency_penalty = {"낮음": 18, "보통": 6, "높음": 0}[seller.digital_fluency]
            product_penalty = max(0, seller.planned_products - 20) * (0.35 if stage == "상품 등록" else 0.05)
            rework_probability = 0.0
            if stage == "서류 확인":
                rework_probability = 0.25 + (0.16 if seller.digital_fluency == "낮음" else 0)
            elif stage == "상품 등록":
                rework_probability = 0.20 + (0.18 if seller.planned_products >= 30 else 0)
            rework_count = 0
            if rng.random() < rework_probability:
                rework_count = 1 + int(rng.random() < 0.16)
            queue_hours = max(2.0, rng.gauss(base_wait + fluency_penalty + product_penalty, base_wait * 0.35))
            active_hours = max(0.5, rng.gauss(base_work + rework_count * 1.8, base_work * 0.2))
            stage_started = current
            completed_at = stage_started + timedelta(hours=queue_hours + active_hours)

            # 관찰 종료 시점 이후이거나 일부 이탈 사례는 미완료로 남긴다.
            dropout_risk = 0.018 + (0.025 if seller.digital_fluency == "낮음" else 0)
            incomplete = completed_at > AS_OF or rng.random() < dropout_risk
            rows.append(
                {
                    "seller_id": seller.seller_id,
                    "stage": stage,
                    "stage_order": order,
                    "started_at": stage_started,
                    "completed_at": pd.NaT if incomplete else completed_at,
                    "queue_hours": round((AS_OF - stage_started).total_seconds() / 3600, 1)
                    if incomplete
                    else round(queue_hours, 1),
                    "active_work_hours": None if incomplete else round(active_hours, 1),
                    "rework_count": rework_count,
                    "status": "진행 중" if incomplete else "완료",
                }
            )
            reached_stage = stage
            if incomplete:
                break
            current = completed_at
        sellers.loc[sellers.seller_id == seller.seller_id, "current_stage"] = reached_stage

    history = pd.DataFrame(rows)
    completed = history[history.stage == "판매 준비 완료"][["seller_id", "completed_at"]].rename(
        columns={"completed_at": "ready_at"}
    )
    sellers.merge(completed, on="seller_id", how="left")
    return history


def generate_inquiries(rng: random.Random, sellers: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    issue_by_stage = {
        "서류 확인": ["서류 보완", "사업자 정보", "검토 일정"],
        "계약": ["계약 절차", "정산 정보", "담당자 확인"],
        "상품 등록": ["상품 등록", "이미지 규격", "카테고리 설정"],
        "판매 준비 완료": ["오픈 일정", "운영 가이드", "마케팅 지원"],
    }
    rows = []
    inquiry_id = 1
    for seller in sellers.itertuples(index=False):
        seller_history = history[history.seller_id == seller.seller_id]
        reworks = int(seller_history.rework_count.sum())
        base_count = rng.choices([0, 1, 2, 3, 4], weights=[18, 33, 27, 15, 7], k=1)[0]
        count = min(6, base_count + reworks + (1 if seller.digital_fluency == "낮음" and rng.random() < 0.55 else 0))
        prior_issue = None
        prior_created = None
        for n in range(count):
            stage_row = seller_history.iloc[min(n + 1, len(seller_history) - 1)]
            stage = stage_row.stage if stage_row.stage in issue_by_stage else "서류 확인"
            issue = weighted_choice(rng, issue_by_stage[stage], [3, 2, 2])
            is_repeat = prior_issue == issue and prior_created is not None and rng.random() < 0.72
            if n > 0 and rng.random() < 0.28:
                issue = prior_issue
                is_repeat = True
            stage_start = pd.Timestamp(stage_row.started_at).to_pydatetime()
            created_at = stage_start + timedelta(hours=max(1, rng.gauss(16 + n * 14, 8)))
            if prior_created and created_at <= prior_created:
                created_at = prior_created + timedelta(hours=rng.randint(6, 30))
            response_hours = max(0.4, rng.gauss(8 + (8 if issue in ["서류 보완", "상품 등록"] else 2), 5))
            resolution_hours = response_hours + max(1.0, rng.gauss(12, 7))
            if created_at > AS_OF:
                continue
            rows.append(
                {
                    "inquiry_id": f"Q{inquiry_id:05d}",
                    "seller_id": seller.seller_id,
                    "stage": stage,
                    "issue_type": issue,
                    "created_at": created_at,
                    "first_response_at": min(created_at + timedelta(hours=response_hours), AS_OF),
                    "resolved_at": pd.NaT
                    if created_at + timedelta(hours=resolution_hours) > AS_OF or rng.random() < 0.05
                    else created_at + timedelta(hours=resolution_hours),
                    "repeat_within_72h": bool(is_repeat and (created_at - prior_created).total_seconds() <= 72 * 3600)
                    if prior_created
                    else False,
                }
            )
            inquiry_id += 1
            prior_issue = issue
            prior_created = created_at
    return pd.DataFrame(rows)


def generate_tasks(rng: random.Random, sellers: pd.DataFrame, history: pd.DataFrame, inquiries: pd.DataFrame) -> pd.DataFrame:
    rows = []
    task_id = 1
    inquiry_counts = inquiries.groupby("seller_id").size().to_dict() if len(inquiries) else {}
    for seller in sellers.itertuples(index=False):
        seller_history = history[history.seller_id == seller.seller_id]
        for stage_row in seller_history.itertuples(index=False):
            if stage_row.stage == "신청":
                continue
            task_count = 1 + int(stage_row.rework_count > 0) + int(rng.random() < 0.22)
            for n in range(task_count):
                release_day = max(0, min(55, (pd.Timestamp(stage_row.started_at).to_pydatetime() - WINDOW_START).days + n))
                effort = max(0.8, rng.gauss(2.4 + stage_row.stage_order * 0.45 + n * 0.5, 1.0))
                rows.append(
                    {
                        "task_id": f"T{task_id:05d}",
                        "seller_id": seller.seller_id,
                        "stage": stage_row.stage,
                        "progress_stage": stage_row.stage_order,
                        "release_day": release_day,
                        "effort_hours": round(effort, 1),
                        "repeat_contact_count": max(0, inquiry_counts.get(seller.seller_id, 0) - 1),
                        "severity": 2 if stage_row.rework_count > 0 else 1,
                    }
                )
                task_id += 1
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Regenerate synthetic CSV inputs without overwriting existing output.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=False)
    rng = random.Random(SEED)
    sellers = generate_sellers(rng)
    history = generate_stage_history(rng, sellers)
    inquiries = generate_inquiries(rng, sellers, history)
    tasks = generate_tasks(rng, sellers, history, inquiries)
    for name, frame in [("sellers", sellers), ("stage_history", history), ("inquiries", inquiries), ("work_tasks", tasks)]:
        frame = frame.copy()
        for column in frame:
            if pd.api.types.is_datetime64_any_dtype(frame[column]):
                frame[column] = frame[column].dt.strftime("%Y-%m-%d %H:%M:%S")
        frame.to_csv(target / (name + ".csv"), index=False, encoding="utf-8-sig")
    print("Generated four synthetic CSV files:", target)

if __name__ == "__main__":
    main()
