# Quick Start: ACM Digital Library 논문 수집

## 🎯 CHI Late Breaking Work 논문 가져오기

### 1단계: ACM에서 DOI 찾기

CHI 2025 Late Breaking Work 검색:
```
https://dl.acm.org/conference/chi
→ CHI '25: Proceedings 찾기
→ Late Breaking Work 섹션
→ 논문 클릭
→ URL에서 DOI 확인 (예: 10.1145/3706599.3719940)
```

### 2단계: 스크립트 실행

```bash
cd tools
python scrape_acm.py <DOI_또는_URL> [paper_id]
```

**예시:**
```bash
# DOI만
python scrape_acm.py 10.1145/3706599.3719940

# Full URL + Custom ID
python scrape_acm.py https://dl.acm.org/doi/10.1145/3706599.3719940 chi2025-lbw-01

# 여러 논문 한번에
python scrape_acm.py 10.1145/3706599.3719940 chi2025-lbw-01
python scrape_acm.py 10.1145/3706599.3719941 chi2025-lbw-02
python scrape_acm.py 10.1145/3706599.3719942 chi2025-lbw-03
```

### 3단계: 결과 확인

```bash
# 생성된 파일들
papers_html/chi2025-lbw-01.html          # 브라우저로 열어서 확인!
papers_json/chi2025-lbw-01.json          # 메타데이터
papers_images/chi2025-lbw-01/            # 다운로드된 이미지들
```

### 4단계: 검토

브라우저로 `papers_html/chi2025-lbw-01.html` 열고:
- ✓ 제목/저자 맞는지
- ✓ 이미지가 잘 보이는지
- ✓ 섹션이 잘 나뉘었는지
- ✓ 본문이 깨지지 않았는지

## 🔄 여러 논문 자동화

```bash
#!/bin/bash
# collect_papers.sh

DOIS=(
    "10.1145/3706599.3719940"
    "10.1145/3706599.3719941"
    "10.1145/3706599.3719942"
    # ... 10개까지
)

cd tools
for i in "${!DOIS[@]}"; do
    paper_num=$(printf "%02d" $((i+1)))
    python scrape_acm.py "${DOIS[$i]}" "chi2025-lbw-$paper_num"
    sleep 2  # 서버에 부담 주지 않기
done
```

## 📊 수집 현황 추적

```bash
# 수집된 논문 개수 확인
ls papers_html/ | wc -l

# 이미지 개수 확인
ls papers_images/*/  | wc -l
```

## ⚠️ 주의사항

1. **Rate Limiting**: 요청 사이에 2초 대기 (스크립트에 내장됨)
2. **네트워크**: 학교 IP나 VPN 사용 권장
3. **저작권**: 연구 목적으로만 사용

## 🆘 문제 해결

**Q: "403 Forbidden" 에러?**
A: VPN 사용하거나 학교 네트워크에서 실행

**Q: 이미지가 안 보여요**
A: 상대 경로 확인 (`../papers_images/...`)

**Q: 일부 내용이 빠졌어요**
A: ACM 페이지 구조 변경 가능 → scrape_acm.py 수정 필요