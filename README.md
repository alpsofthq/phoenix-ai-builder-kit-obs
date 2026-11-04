# Phoenix AI Builder Kit · OBA RUN Season 2

[English](docs/en.md) · [日本語](docs/ja.md)

2026년 11월 7일 OBA 해커톤 참가자를 위한 Phoenix AI DATA API·MCP 가이드와 실행 예제입니다. 한국 시세와 한국·미국 재무·공시·스크리너·일정 데이터를 조합해 금융 서비스를 만들어 보세요.

이 저장소가 **Builder 참가자 안내의 기준 문서**입니다. 계정·키·사용량은 [개발자 포털](https://openapi.chickstockfi.com/login)에서 관리하고, 상세 필드는 [DATA API 레퍼런스](https://openapi.chickstockfi.com/docs)를 참고하세요. 전체 레퍼런스에 있는 모든 기능이 Builder에 포함되는 것은 아닙니다.

## 먼저 확인하세요

| 항목 | 안내 |
| --- | --- |
| 계정 | 행사 코드·이메일 인증으로 신청하는 팀별 계정, 활성 DATA 키 최대 2개 |
| 키 | `ck_live_`로 시작하는 DATA API 키. REST·MCP에서 같은 키 사용 |
| REST Base URL | `https://api.chickstockfi.com/openapi/v1` |
| DATA MCP | `https://api.chickstockfi.com/openapi/v1/mcp` |
| 사전 테스트 | 계정 활성화부터 **11월 7일 00:00 KST 전까지** · 팀당 누적 **1,000회 / 10 RPM** |
| 본 행사 | **2026-11-07 00:00 ≤ 이용 시각 < 2026-11-08 00:00 KST** · 팀당 누적 **10,000회 / 20 RPM** |
| 동시 요청 | 팀당 최대 2개. 혼잡 시 행사 전체 한도가 추가 적용됩니다. |

모든 키·REST·MCP·문서 시험 호출이 팀 한도를 공유합니다. 사전 테스트 사용량은 본 행사 한도에서 차감하지 않습니다. 키 교체나 자정 경과로 각 단계의 누적 한도가 초기화되지 않습니다. 종료 후에는 데이터 조회가 중단됩니다.

**PRO·뉴스룸·뉴스/뉴스와이어·미국/일본 시세 직접 조회·신규 AI 생성·웹훅은 제공하지 않습니다.** 이미 검토·공개된 한국·미국 공시 분석은 조회할 수 있습니다. [제공 범위 전체 보기 →](docs/coverage.md)

## 3분 시작

1. 팀 대표 한 명이 [Builder 신청](https://openapi.chickstockfi.com/request?product=builder)에서 주최 측이 안내한 신청 코드를 입력합니다. 이메일 인증 후 비밀번호를 설정하고, [포털](https://openapi.chickstockfi.com/login)에 로그인해 DATA 키를 만듭니다. 이미 계정을 받은 팀은 기존 계정을 그대로 사용하세요.
2. 이 저장소를 복제하고 `.env.example`을 `.env`로 복사합니다. `.env`의 `YOUR_TEAM_KEY`를 **본인 팀의 DATA 키**로 바꿉니다.
3. Node.js 22 이상 또는 Python 3.11 이상에서 아래 예제를 실행합니다. 추가 라이브러리는 필요 없습니다.

```sh
git clone https://github.com/alpsofthq/phoenix-ai-builder-kit-obs.git
cd phoenix-ai-builder-kit-obs
cp .env.example .env
# .env를 편집한 뒤, macOS/Linux 터미널에서 환경변수를 불러옵니다.
set -a
. ./.env
set +a

node examples/javascript/quickstart.mjs usage
# 또는
python3 examples/python/quickstart.py usage
```

Windows PowerShell에서는 `$env:PHOENIX_DATA_KEY = '본인 팀의 키'`로 환경변수를 설정한 뒤 예제를 실행하세요. 키를 채팅·화면 녹화·저장소에 노출하지 마세요.

첫 호출 `GET /key`는 현재 권한과 사용량을 확인하며 DATA 조회 총량을 차감하지 않습니다. 각 예제는 **한 번 실행할 때 한 요청만** 보냅니다. 다음 예제를 한꺼번에 실행하지 말고 필요한 것부터 확인하세요.

```sh
node examples/javascript/quickstart.mjs quote 005930
node examples/javascript/quickstart.mjs financials 005930
node examples/javascript/quickstart.mjs disclosures 005930
node examples/javascript/quickstart.mjs us-filings AAPL
node examples/javascript/quickstart.mjs screener US
node examples/javascript/quickstart.mjs earnings
```

Python도 동일한 인자를 받습니다. 예: `python3 examples/python/quickstart.py screener KR`.

공시 목록에서 받은 ID로 이미 공개된 분석을 조회할 수 있습니다.

```sh
node examples/javascript/quickstart.mjs analysis '목록에서 받은 공시 ID'
```

한국 ID는 14자리 DART 접수번호, 미국 ID는 `TICKER:ACCESSION`입니다. 예제가 URL 인코딩을 처리합니다. **분석이 없는 경우 `404 ANALYSIS_NOT_AVAILABLE`이며, 이 요청으로 새 분석이 생성되지 않습니다.**

신청 코드는 API 키가 아닙니다. 신청 코드를 공개 저장소에 넣지 마세요. 이메일 인증번호는 10분 동안 유효하고, 다섯 번 틀리면 새 번호를 받아야 합니다. 같은 이메일의 재신청은 비밀번호나 사용 한도를 초기화하지 않습니다. 기존 유료·PoC 계정 또는 중복 팀이 확인되면 담당자 확인이 필요합니다.

## MCP로 연결하기

[MCP 가이드](docs/mcp.md)에 Claude Code·Cursor 설정 파일과 첫 질문 예제를 준비했습니다. Builder는 **DATA MCP 주소와 DATA 키**를 사용합니다. PRO MCP·OAuth·`ck_pers_` 키는 대상이 아닙니다.

## 무엇을 만들 수 있나요?

| 아이디어 | 조합할 데이터 |
| --- | --- |
| 기업 비교 대시보드 | 재무제표 + 재무지표 + 매출 구성 |
| 관심 종목 공시 도우미 | 한국/미국 공시 목록 + 이미 공개된 분석 + 원문 링크 |
| 조건 기반 기업 탐색 | 스크리너 + 섹터·섹터 순위 |
| 투자 일정 보드 | 미국 실적 일정 + 한국 IR·IPO 일정 + 경제 일정 |

날짜·단위·통화·출처와 `meta.as_of`를 표시하고, 빈 데이터와 0을 구분하세요. 스크리너 안에 제공되는 가격·시가총액은 사용할 수 있지만, 이를 미국 시세 직접 조회·가격 이력·스트리밍 권한으로 해석하면 안 됩니다.

## 문서와 지원

- [제공 범위·호출 한도·이용 조건](docs/coverage.md)
- [MCP 연결](docs/mcp.md)
- [오류 처리·페이지네이션·FAQ](docs/troubleshooting.md)
- [DATA API 레퍼런스](https://openapi.chickstockfi.com/docs) · [공식 OpenAPI JSON](https://api.chickstockfi.com/openapi/v1/openapi.json)
- 일반 연동 질문: [GitHub Issues](https://github.com/alpsofthq/phoenix-ai-builder-kit-obs/issues)
- 계정·권한·행사 후 도입 문의: [문의 양식](https://openapi.chickstockfi.com/request) 또는 help@alpsoft.io

문의에는 발생 시각·요청 경로·HTTP 상태·오류 코드·요청 ID를 적어 주세요. **키·비밀번호·세션·전체 응답 데이터는 올리지 마세요.**

프로젝트 코드와 결과 화면 데모는 공개할 수 있습니다. 데이터 출처는 **Phoenix AI**로 표시해 주세요. 원본 응답 전체·데이터 덤프·재배포용 데이터셋 공개와 행사 후 계속 운영은 별도 협의가 필요합니다. [서비스 이용약관](https://openapi.chickstockfi.com/terms)을 함께 확인하세요.

문서 확인일: 2026-11-04 · DATA API 명세 1.18.0 기준
