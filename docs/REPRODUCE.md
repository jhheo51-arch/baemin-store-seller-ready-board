# 셀러 레디 보드 계산 재현

[프로젝트 소개로 돌아가기](../README.md)

PDF와 Excel은 운영 판단을 설명하는 가상 사례 12건을 사용합니다. 계산 노트북은 별도로 만든 가상 판매자 240곳 자료를 사용합니다. 두 표본을 같은 운영 성과로 합치지 않습니다.

## 실행

Python 3.12에서 저장소 최상위 폴더의 터미널에 입력합니다. 원본 CSV와 제출 자료를 덮어쓰지 않습니다.

```sh
python -m pip install -r requirements.txt
python scripts/check_repository.py
python -m unittest discover -s tests -v
python scripts/check_notebook.py
```

노트북은 공개 CSV에서 정책 세 가지를 다시 계산하고 저장된 비교 결과와 일치하는지 검사합니다. 자동 검사는 원자료 재생성, 계산 결과, 작은 수작업 사례, 빈 입력과 잘못된 입력도 확인합니다.

## 원자료 생성

```sh
python analysis/generate_data.py --output-dir reproduced-data
```

기존 출력 폴더가 있으면 생성을 거절합니다. 생성 규칙과 난수 시작값을 고정해 공개 CSV 네 개를 다시 만들 수 있습니다.

## 계산을 읽는 기준

- 56일 동안 하루 80시간의 가상 처리 여력을 각 정책에 동일하게 적용합니다.
- `sla_3day_rate`는 완료 업무 중 3일 안에 처리한 비율입니다. 전체 접수 업무를 분모로 하는 운영 목표 지표와 혼용하지 않습니다.
- `ready_stage_sla_3day_rate`는 상품 등록과 판매 준비 단계인 `progress_stage >= 4`를 대상으로 합니다.
- 재문의 수는 가상 자료의 전체 기간 집계값입니다. 각 판단 시점에 실제로 알 수 있었던 정보만 사용한 모형은 아닙니다.
- 실제 팀에서 대기시간이나 재문의가 줄었다는 결과로 해석하지 않습니다.

상세 정렬 기준과 계산은 [분석 노트북](../analysis/seller-onboarding-analysis.ipynb), 항목 정의는 [데이터 항목 설명](data-dictionary.md)을 참고하세요.
