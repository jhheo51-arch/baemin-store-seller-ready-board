# 셀러 레디 보드

판매자의 입점 준비에서 먼저 볼 문제를 고르고, 다음 행동과 완료 기준을 남기는 운영 보드입니다.

[소개 PDF](SELLER-READY-BOARD-PORTFOLIO.pdf) · [Excel 운영표](SELLER-READY-BOARD-OPERATIONS.xlsx) · [웹 화면 파일](BAEMIN-STORE-OPERATIONS-PORTFOLIO.html)

배민스토어 공식 가이드와 채용공고를 바탕으로 만든 개인 프로젝트입니다. 판매자와 운영 수치는 가상입니다.

## 핵심 설계

**정보 오류 → 장기 대기와 재문의 → 오픈 임박 → 담당자 미배정**

단순 등록보다 실제로 주문을 받을 준비가 됐는지를 완료 기준으로 정했습니다. Excel과 웹 화면에서 대기일, 재문의, 오픈일과 담당자를 바꾸면 먼저 볼 신호가 다시 계산됩니다.

## 검증 범위

PDF와 Excel의 가상 사례 12건에 같은 판단 기준을 적용했습니다. 별도 가상 판매자 240곳으로 처리 정책 3개를 재계산하고, 원자료 생성과 계산 검사 5개를 통과했습니다.

‘3일 내 처리율’의 분모는 완료 업무이며, 미완료 업무는 별도로 셉니다. 실제 팀의 처리시간, 재문의 감소와 기록 부담은 아직 측정하지 않았습니다.

## 자료 안내

| 보고 싶은 내용 | 문서 |
|---|---|
| 문제와 판단 근거 | [기획서와 공식 출처](docs/PRD.md) |
| 운영과 2주 시험 | [운영 문서](docs/operations-runbook.md) / [판매자 안내 초안](docs/seller-onboarding-guide.md) |
| 계산과 재현 | [계산 과정](analysis/seller-onboarding-analysis.ipynb) / [원자료](data/) / [항목 설명](docs/data-dictionary.md) / [재현 안내](docs/REPRODUCE.md) |

<details>
<summary>화면 미리보기</summary>

![셀러 레디 보드 프로젝트 화면](assets/project-overview.png)

</details>

<details>
<summary>직접 실행하기와 자동 검사</summary>

내용을 읽으려면 위 PDF를, 입력을 바꿔 보려면 Excel을 여세요. 웹 화면은 저장소를 내려받은 뒤 `BAEMIN-STORE-OPERATIONS-PORTFOLIO.html`을 브라우저로 엽니다.

**계산 재실행 — Python 3.12**

저장소 폴더의 터미널에서 실행합니다.

```sh
python -m pip install -r requirements.txt
python scripts/check_repository.py
python -m unittest discover -s tests -v
python scripts/check_notebook.py
```

원자료 생성 명령과 계산 가정은 [재현 안내](docs/REPRODUCE.md)에 있습니다.

</details>
