# Reading Experiment with LLM

LLM 보조 환경에서 학술 논문 읽기 행동 관찰 실험 시스템

## 프로젝트 구조

```
reading-experiment/
├── papers/              # 원본 PDF 파일들 (방법 B용)
├── papers_html/         # 변환된 HTML 파일들 (검토용)
├── papers_json/         # 논문 메타데이터 (섹션 정보 등)
├── papers_images/       # ACM에서 다운로드한 이미지들
├── tools/               # 변환 및 통합 도구들
│   ├── scrape_acm.py         # ACM DL → HTML (추천!)
│   ├── convert_paper.py      # PDF → HTML 변환기
│   └── integrate_papers.py   # HTML → 실험 시스템 통합
└── experiment.html      # 최종 실험 시스템
```

## 사용 방법

### 방법 A: ACM Digital Library에서 가져오기 (추천! ⭐)

**CHI Late Breaking Work는 ACM에 있습니다!**

```bash
cd tools

# DOI만으로 가져오기
python scrape_acm.py 10.1145/3706599.3719940

# 또는 전체 URL로
python scrape_acm.py https://dl.acm.org/doi/10.1145/3706599.3719940 chi2025-lbw-01

# 결과: papers_html/에 HTML 생성 + papers_images/에 이미지 저장
```

**장점:**
- ✅ 이미지 자동 다운로드
- ✅ 수식, 표, 그림 모두 포함
- ✅ 깔끔한 레이아웃
- ✅ 섹션 자동 인식

### 방법 B: PDF → HTML 변환 (대안)

```bash
# papers/ 폴더에 PDF 파일 추가
cp your_paper.pdf papers/

# HTML로 변환
cd tools
python convert_paper.py ../papers/your_paper.pdf [optional-paper-id]

# 결과 확인: papers_html/에 생성된 HTML 파일을 브라우저로 열어서 검토
```

**검토 사항:**
- ✓ 제목과 저자가 올바르게 추출되었는지
- ✓ 섹션이 제대로 인식되었는지
- ✓ 내용이 읽기 편한지
- ✓ 텍스트 추출 오류가 없는지

### 2단계: 실험 시스템에 통합

검토 완료된 논문들을 실험 시스템에 통합:

```bash
cd tools
python integrate_papers.py

# 또는 특정 논문만 통합
python integrate_papers.py paper1 paper2 paper3
```

### 3단계: 실험 실행

생성된 `experiment.html`을 브라우저로 열기

## 논문 추가 예시

```bash
# 1. PDF 복사
cp "CHI 2025 Paper.pdf" papers/chi2025-paper.pdf

# 2. 변환
cd tools
python convert_paper.py ../papers/chi2025-paper.pdf chi2025-paper

# 3. 브라우저에서 papers_html/chi2025-paper.html 검토

# 4. 문제없으면 통합
python integrate_papers.py chi2025-paper

# 5. experiment.html 실행하여 테스트
```

## 팁

- **Paper ID 규칙**: 소문자, 하이픈(-) 사용, 공백 없음
- **섹션 감지 실패시**: `convert_paper.py`의 `section_keywords` 리스트에 추가
- **텍스트 추출 문제**: PDF 품질 확인 (스캔본은 OCR 필요)

## 실험 데이터

실험 완료 후 다음 데이터 수집:
- 로그 데이터: localStorage의 `experimentEvents`
- 분석 도구: `admin_dashboard.html` 사용