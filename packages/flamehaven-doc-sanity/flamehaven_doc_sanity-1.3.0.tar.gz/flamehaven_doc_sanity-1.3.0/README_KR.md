# Flamehaven-Doc-Sanity

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

드리프트 감지 및 다국어 지원을 갖춘 Python 기반 문서 검증 프레임워크입니다.

## 주요 기능

- **문서 검증**: 마크다운 파일의 구조, 완전성, 품질 검사
- **드리프트 감지**: Jensen-Shannon Divergence를 사용한 설정 변경 모니터링
- **다국어 번역**: 한국어/영어 문서 자동 번역 워크플로우
- **플러그인 시스템**: 확장 가능한 검증기 아키텍처
- **웹 대시보드**: Flask 기반 모니터링 인터페이스
- **CI/CD 통합**: 자동화된 검증을 위한 GitHub Actions 워크플로우

## 설치

### PyPI에서 설치 (권장)

```bash
pip install flamehaven-doc-sanity
```

### 소스에서 설치

```bash
git clone https://github.com/flamehaven01/Flamehaven-Doc-Sanity.git
cd Flamehaven-Doc-Sanity
pip install -e .
```

## 빠른 시작

### 문서 검증

```bash
doc-sanity check README.md
```

### 문서 번역

```bash
doc-sanity translate README.md --target-lang ko
```

### 설정 드리프트 확인

```bash
doc-sanity guard
```

### 대시보드 실행

```bash
doc-sanity dashboard
```

## 사용 예제

### 기본 검증

```bash
# 단일 파일 검사
doc-sanity check docs/architecture.md

# 엄격한 모드로 검사
doc-sanity check --governance-mode strict README.md

# 상세 리포트 표시
doc-sanity check --verbose README.md
```

### 번역 워크플로우

```bash
# 한국어로 번역
doc-sanity translate README.md --target-lang ko --output README_KR.md

# 디렉토리 일괄 번역
doc-sanity translate docs/ --target-lang ko
```

### 드리프트 감지

```bash
# 기준선 대비 검사
doc-sanity guard

# 기준선 업데이트
doc-sanity guard --update-baseline
```

## 설정

프로젝트 루트에 `.doc-sanity.yaml` 파일을 생성하세요:

```yaml
validators:
  - structure
  - completeness
  - quality

governance:
  mode: balanced  # conservative, balanced, strict
  threshold: 0.85

drift_detection:
  enabled: true
  baseline: config/golden_baseline.yaml
  threshold: 0.05
```

## 아키텍처

```
flamehaven_doc_sanity/
├── validators/         # 문서 검증 로직
├── governance/         # 정책 시행
│   ├── driftlock_guard.py   # 설정 드리프트 감지
│   └── policy_enforcer.py    # 거버넌스 규칙
├── i18n/               # 번역 시스템
├── orchestrator/       # 검증 조정
├── plugins/            # 확장 가능 플러그인 시스템
└── dashboard/          # 웹 인터페이스
```

## CLI 명령어

| 명령어 | 설명 |
|---------|-------------|
| `check` | 문서 검증 |
| `translate` | 문서 번역 |
| `guard` | 설정 드리프트 확인 |
| `dashboard` | 웹 UI 실행 |
| `version` | 버전 정보 표시 |

## 개발

### 사전 요구사항

- Python 3.9+
- pip
- git

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/flamehaven01/Flamehaven-Doc-Sanity.git
cd Flamehaven-Doc-Sanity

# 개발 의존성과 함께 설치
pip install -e ".[dev]"

# 테스트 실행
pytest tests/

# 코드 포매팅 확인
black --check flamehaven_doc_sanity tests
isort --check-only flamehaven_doc_sanity tests
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/ -v

# 커버리지와 함께 실행
pytest tests/ --cov=flamehaven_doc_sanity

# 특정 테스트 파일 실행
pytest tests/test_validators.py
```

### 코드 품질

```bash
# 코드 포맷
black flamehaven_doc_sanity tests
isort flamehaven_doc_sanity tests

# 린트
flake8 flamehaven_doc_sanity tests
```

## 거버넌스 모드

- **conservative**: 기본 검증, 최소한의 검사
- **balanced**: 표준 검증 (기본값)
- **strict**: 엄격한 규칙을 적용한 종합 검증

## 플러그인 개발

기본 플러그인을 확장하여 커스텀 검증기를 만드세요:

```python
from flamehaven_doc_sanity.plugins.base import BasePlugin, ValidationResult

class MyValidator(BasePlugin):
    def validate(self, content: str) -> ValidationResult:
        # 검증 로직
        return ValidationResult(
            passed=True,
            score=0.95,
            message="검증 통과"
        )
```

## 설정 드리프트 감지

드리프트 감지 시스템은 Jensen-Shannon Divergence를 사용하여 설정 변경을 측정합니다:

- **JSD < 0.05**: 유의미한 드리프트 없음
- **JSD 0.05-0.15**: 경미한 드리프트, 검토 권장
- **JSD > 0.15**: 상당한 드리프트, 조치 필요

## 대시보드

다음 명령어를 실행한 후 `http://localhost:5000`에서 웹 대시보드에 접근하세요:

```bash
doc-sanity dashboard
```

기능:
- 실시간 검증 상태
- 드리프트 모니터링 그래프
- 번역 큐 관리
- 기록 메트릭

## CI/CD 통합

### GitHub Actions 예제

```yaml
name: Documentation Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install doc-sanity
        run: pip install flamehaven-doc-sanity

      - name: Validate documentation
        run: doc-sanity check README.md
```

## API 레퍼런스

### Python API

```python
from flamehaven_doc_sanity import DocumentValidator

# 검증기 초기화
validator = DocumentValidator(mode='balanced')

# 문서 검증
result = validator.validate_file('README.md')

if result.passed:
    print(f"검증 통과: {result.score}")
else:
    print(f"검증 실패: {result.message}")
```

## 테스트

현재 테스트 커버리지: ~45%

테스트 스위트:
- 단위 테스트: 40개
- 통합 테스트: 10개
- 성능 테스트: 4개

## 성능

일반적인 검증 시간:
- 작은 파일 (<10KB): <50ms
- 중간 파일 (10-100KB): <200ms
- 큰 파일 (>100KB): <500ms

## 기여하기

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/my-feature`)
3. 변경사항 커밋 (`git commit -m 'Add my feature'`)
4. 브랜치에 푸시 (`git push origin feature/my-feature`)
5. Pull Request 열기

### 기여 가이드라인

- PEP 8 스타일 가이드 준수
- 새 기능에 대한 테스트 추가
- 문서 업데이트
- 모든 테스트 통과 확인

## 변경 로그

릴리스 히스토리는 [CHANGELOG.md](CHANGELOG.md)를 참조하세요.

## 로드맵

- [ ] 추가 언어 지원 (일본어, 중국어)
- [ ] 고급 의미 분석
- [ ] 인기 문서 도구 통합 (Sphinx, MkDocs)
- [ ] 머신러닝 기반 품질 점수
- [ ] VSCode 확장 프로그램

## 라이선스

이 프로젝트는 MIT 라이선스로 배포됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 작성자

- **Flamehaven** - 초기 작업 - [@flamehaven01](https://github.com/flamehaven01)

## 감사의 글

- Python 3.9+로 구축
- CLI 인터페이스에 Click 사용
- 설정 관리에 PyYAML 사용
- 대시보드에 Flask 사용
- 테스트 프레임워크에 pytest 사용

## 지원

- 문서: [GitHub Wiki](https://github.com/flamehaven01/Flamehaven-Doc-Sanity/wiki)
- 이슈: [GitHub Issues](https://github.com/flamehaven01/Flamehaven-Doc-Sanity/issues)
- 토론: [GitHub Discussions](https://github.com/flamehaven01/Flamehaven-Doc-Sanity/discussions)

## FAQ

**Q: 어떤 파일 형식이 지원되나요?**
A: 현재 마크다운(.md) 파일을 지원합니다. 드리프트 감지를 위한 YAML 설정 파일도 지원합니다.

**Q: 드리프트 감지는 어떻게 작동하나요?**
A: Jensen-Shannon Divergence를 사용하여 현재 설정과 기준선을 비교하여 통계적 차이를 측정합니다.

**Q: 프로덕션에서 사용할 수 있나요?**
A: 버전 1.3.0은 기본 검증 워크플로우에서 안정적입니다. 프로덕션 사용을 위해서는 철저한 테스트를 권장합니다.

**Q: 버그는 어떻게 보고하나요?**
A: [GitHub Issues](https://github.com/flamehaven01/Flamehaven-Doc-Sanity/issues)에 이슈를 등록해주세요.

---

**버전**: 1.3.0
**상태**: 활발한 개발 중
**Python**: 3.9+
