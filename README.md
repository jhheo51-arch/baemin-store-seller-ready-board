# 셀러 레디 보드

**판매자의 입점 준비에서 먼저 볼 문제를 고르고, 다음 행동과 완료 기준까지 남기는 운영 보드입니다.**

[포트폴리오 PDF](SELLER-READY-BOARD-PORTFOLIO.pdf) | [Excel 운영표](SELLER-READY-BOARD-OPERATIONS.xlsx) | [웹 화면 파일](BAEMIN-STORE-OPERATIONS-PORTFOLIO.html)

배민스토어 운영지원 공고와 공식 가이드를 읽고 만든 개인 프로젝트입니다. 판매자와 운영 수치는 가상이며 실제 내부 자료는 사용하지 않았습니다.

![셀러 레디 보드 프로젝트 화면](assets/project-overview.png)

## 어떤 판단을 돕나요?

단순 등록보다 **실제로 주문을 받을 준비가 됐는지**를 완료 기준으로 정했습니다.

| 먼저 볼 신호 | 확인할 내용 |
|---|---|
| 정보 오류 | 상품과 운영 정보가 정확한가 |
| 장기 대기와 재문의 | 같은 문제로 오래 기다리거나 다시 문의하는가 |
| 오픈 임박 | 판매 시작 전에 필요한 준비가 끝나는가 |
| 담당자 미배정 | 누가 다음 행동을 언제 할지 정해졌는가 |

Excel과 웹 화면에서 대기일, 재문의, 오픈일과 담당자를 바꾸면 우선 신호가 다시 계산됩니다.

## 어디까지 확인했나요?

- PDF와 Excel의 가상 사례 12건에 같은 판단 기준을 적용했습니다.
- 별도의 가상 판매자 240곳 자료로 처리 정책 3개를 다시 계산해 저장된 결과와 일치하는지 검사합니다. 원자료 생성과 계산 검사 5개도 통과했습니다.
- 실제 팀의 처리시간, 재문의 감소와 기록 부담은 아직 측정하지 않았습니다. [2주 운영 시험 계획](docs/operations-runbook.md)으로 확인할 항목을 정리했습니다.

정책 비교표의 ‘3일 내 처리율’은 **완료한 업무 중** 3일 안에 처리한 비율입니다. 미완료 업무는 따로 셉니다.

## 직접 확인하기

내용을 읽으려면 위 PDF를, 입력을 바꿔 보려면 Excel을 여세요. 웹 화면은 저장소를 내려받은 뒤 `BAEMIN-STORE-OPERATIONS-PORTFOLIO.html`을 브라우저로 엽니다.

<details>
<summary>계산 재실행 — Python 3.12</summary>

저장소 폴더의 터미널에서 실행합니다.

```sh
python -m pip install -r requirements.txt
python scripts/check_repository.py
python -m unittest discover -s tests -v
python scripts/check_notebook.py
```

원자료 생성 명령과 계산 가정은 [재현 안내](docs/REPRODUCE.md)에 있습니다.

</details>

## 더 살펴보기

- [기획서와 공식 출처](docs/PRD.md): 문제를 고른 이유, 우선순위와 완료 기준
- [운영 문서](docs/operations-runbook.md) / [판매자 안내 초안](docs/seller-onboarding-guide.md)
- [계산 과정](analysis/seller-onboarding-analysis.ipynb) / [가상 원자료](data/) / [데이터 항목 설명](docs/data-dictionary.md)
