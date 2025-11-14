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

### Firebase Firestore 데이터베이스 구조

#### 참가자 문서 구조 (`users/{participantId}`)

```
users/P001/
├── participantId: "P001"
├── condition: "experiment_mode"         # "with_llm" | "without_llm" | "experiment_mode"
├── paper: "chi2025-lbw-01"
├── mode: "experiment"                   # "experiment" | "test"
├── sessionOrder: ['with_llm', 'without_llm']  # 실험 모드일 때 세션 순서
├── createdAt: Timestamp
├── completedAt: Timestamp
│
├── preSurvey: {                         # 사전 설문 응답
│   ├── participantId: "P001"
│   ├── condition: "experiment_mode"
│   ├── paper: "chi2025-lbw-01"
│   ├── mode: "experiment"
│   ├── sessionOrder: ['with_llm', 'without_llm']
│   ├── demographics: {
│   │   ├── gender: "male"
│   │   ├── age: 25
│   │   └── education: "master-enrolled"
│   │   }
│   ├── researchExperience: {
│   │   ├── major: "컴퓨터공학과"
│   │   ├── semester: "2"
│   │   ├── hasHciSubmissionExperience: false
│   │   └── hasNonHciSubmissionExperience: true
│   │   }
│   ├── llmUsage: {
│   │   ├── frequency: "daily"
│   │   └── purposes: [
│   │       {
│   │           name: "논문 읽기 / 정리",
│   │           otherText: null,
│   │           trust: 4,           # 1-5
│   │           usefulness: 5       # 1-5
│   │       },
│   │       ...
│   │       ]
│   │   }
│   └── surveyCompletedAt: "2025-11-14T10:30:00.000Z"
│   }
│
├── postSurvey: {                        # 사후 설문 응답
│   ├── taskExperience: {
│   │   ├── difficulty: 4            # LLM 사용 시 이해 용이성
│   │   ├── engagement: 5            # LLM의 복잡한 개념 해석 도움
│   │   ├── confidence: 3            # LLM 없이 집중 유지 어려움
│   │   └── satisfaction: 4          # LLM 사용 시 정보량 부담 감소
│   │   }
│   ├── llmUsage: {                  # with_llm 조건일 때만 존재
│   │   ├── helpfulness: 5           # LLM이 개념 이해에 도움
│   │   ├── trust: 4                 # LLM 응답 신뢰도
│   │   ├── influence: 5             # LLM 사용 만족도
│   │   ├── advantages: "용어 설명이 명확해서 좋았음"
│   │   └── disadvantages: "가끔 맥락을 벗어난 답변"
│   │   }
│   ├── overallFeedback: {
│   │   ├── strategies: "초록 먼저 읽고 그림 중심으로 이해"
│   │   ├── challenges: "낯선 용어가 많았음"
│   │   ├── improvements: "논문 내 용어집 제공"
│   │   └── additionalComments: "전반적으로 만족스러웠음"
│   │   }
│   ├── bankAccount: "신한 110-125-****** 김ㅁㅁ"
│   └── surveyCompletedAt: "2025-11-14T12:00:00.000Z"
│   }
│
└── experiments/                         # 하위 컬렉션 (세션별 실험 데이터)
    ├── session-1-xxx/
    └── session-2-yyy/
```

#### 실험 세션 구조 (`users/{participantId}/experiments/{sessionId}`)

```
experiments/session-1-with_llm-1731567000000/
├── participantId: "P001"
├── sessionId: "session-1-with_llm-1731567000000"
├── condition: "with_llm"                # "with_llm" | "without_llm"
├── paper: "chi2025-lbw-01"
├── startedAt: Timestamp
├── completedAt: Timestamp
├── status: "completed"                  # "in_progress" | "completed"
│
├── reading: {                           # Reading Phase (30분)
│   ├── duration: 1800000                # ms (30분)
│   ├── tabTimes: {
│   │   ├── reading: 1200000             # Reading 탭 사용 시간 (ms)
│   │   └── ai: 600000                   # AI 탭 사용 시간 (ms, with_llm만)
│   │   }
│   ├── classificationSummary: {
│   │   ├── reading: {                   # 5초 이상 멈춤
│   │   │   ├── count: 45
│   │   │   ├── totalDuration: 900000    # ms
│   │   │   ├── sections: ["Abstract", "Introduction", "Methods", ...]
│   │   │   ├── percentage: "50.0%"      # 전체 이벤트 중 비율
│   │   │   ├── durationSec: "900초"
│   │   │   └── timePercentage: "50.0%"  # 전체 시간 중 비율
│   │   │   }
│   │   ├── scanning: {                  # 2-5초 멈춤
│   │   │   ├── count: 30
│   │   │   ├── totalDuration: 300000
│   │   │   └── ...
│   │   │   }
│   │   ├── scrolling: {                 # 2초 미만
│   │   │   ├── count: 60
│   │   │   ├── totalDuration: 180000
│   │   │   └── ...
│   │   │   }
│   │   └── llm: {                       # AI 탭 사용 (with_llm만)
│   │       ├── count: 12
│   │       ├── totalDuration: 420000
│   │       └── ...
│   │       }
│   │   }
│   ├── sectionAnalysis: {
│   │   "Abstract": {
│   │       reading: 60000,              # ms
│   │       scanning: 20000,
│   │       scrolling: 5000
│   │   },
│   │   "Introduction": {
│   │       reading: 180000,
│   │       scanning: 40000,
│   │       scrolling: 10000
│   │   },
│   │   ...
│   │   }
│   ├── events: [                        # 모든 읽기 이벤트 배열
│   │   {
│   │       timestamp: 1731567012345,
│   │       eventType: "scroll_action",  # "scroll_action" | "tab_switch" | "llm_activity"
│   │       phase: "reading",
│   │       timeSinceLast: 5234,         # ms
│   │       participantId: "P001",
│   │       sessionId: "session-1-...",
│   │       condition: "with_llm",
│   │       paper: "chi2025-lbw-01",
│   │       scrollY: 1250,
│   │       sectionBeforeScroll: "Introduction",
│   │       sectionAfterScroll: "Introduction",
│   │       classification: "reading",   # "reading" | "scanning" | "scrolling"
│   │       pauseDuration: 5234,         # 멈춤 시간 (ms)
│   │       scrollDuration: 156,         # 스크롤 동작 시간 (ms)
│   │       isTabSwitch: false,
│   │       isFinalSegment: false
│   │   },
│   │   {
│   │       timestamp: 1731567045678,
│   │       eventType: "tab_switch",     # 탭 전환 이벤트 (with_llm만)
│   │       from: "reading",
│   │       to: "ai",
│   │       timeOnPreviousTab: 33333,    # ms
│   │       ...
│   │   },
│   │   {
│   │       timestamp: 1731567078901,
│   │       eventType: "llm_activity",   # LLM 타이핑 이벤트 (with_llm만)
│   │       classification: "typing",    # "typing" | "none-typing"
│   │       duration: 15000,             # ms
│   │       ...
│   │   },
│   │   ...
│   │   ]
│   └── completedAt: Timestamp
│   }
│
├── llmInteraction: {                    # LLM 대화 데이터 (with_llm만)
│   ├── messages: [
│   │   {
│   │       question: "What is grounded theory?",
│   │       questionTime: 1731567050000,
│   │       answer: "Grounded theory is...",
│   │       answerTime: 1731567052000,
│   │       responseTime: 2000           # ms
│   │   },
│   │   ...
│   │   ]
│   ├── totalQueries: 12
│   └── avgResponseTime: 2500            # ms
│   }
│
├── quiz: {                              # Quiz Phase (15분)
│   ├── answers: {
│   │   "q1": "option_a",
│   │   "q2": "option_c",
│   │   ...
│   │   }
│   ├── duration: 900000                 # ms (15분)
│   └── submittedAt: Timestamp
│   }
│
└── review: {                            # Review Phase (20분)
    ├── rating: 4                        # 1-5
    ├── strengths: "Novel approach to LLM evaluation"
    ├── weaknesses: "Limited sample size"
    ├── suggestions: "Consider more diverse user groups"
    ├── duration: 1200000                # ms (20분)
    └── submittedAt: Timestamp
    }
```

### 데이터 수집

실험 완료 후 다음 데이터 수집:
- **Firebase**: `users/{participantId}` 및 `experiments/{sessionId}` 문서
- **백업**: localStorage의 `experimentEvents`
- **분석 도구**: `admin.html` 사용