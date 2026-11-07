# Builder 제공 범위와 이용 조건

[처음으로](../README.md) · [English](en.md) · [日本語](ja.md)

이번 Builder는 OBA RUN Season 2 프로젝트 제작·데모용 **DATA API + DATA MCP** 이용권입니다. 일반 기업용 API 계약이나 PRO 이용권과 구분됩니다. 실제 키의 시장·단계·잔여량은 `GET /key` 또는 포털에서 확인하세요.

## 제공 데이터

아래 경로 앞에는 `https://api.chickstockfi.com/openapi/v1`을 붙입니다. 쿼리 필드·단위·응답 스키마는 [공식 명세](https://api.chickstockfi.com/openapi/v1/openapi.json)를 따릅니다.

| 데이터 | 시장 | 대표 경로 또는 쿼리 |
| --- | --- | --- |
| 종목 검색 | KR | `GET /symbols?q=삼성전자&limit=2` (검색어 URL 인코딩) |
| 현재 시세·일별 가격 | KR | `GET /quotes/005930`, `GET /quotes/005930/daily` |
| 재무·지표·매출 구성·배당·공시 가이던스 | KR, US | `GET /companies/{symbol}/financials`, `/metrics`, `/segments`, `/dividends`, `/guidance`, `/net-income-split` |
| 스크리너·섹터·섹터 순위 | KR, US | `GET /screener`, `GET /sectors`; 기업 업종 조회는 `POST /query`: `sector` |
| 공매도 거래·보고 잔고 | KR, US | `GET /companies/{symbol}/short-selling?series=volume` 또는 `series=balance` |
| 공시 목록·원문 | KR | `GET /disclosures?symbol=005930`, `GET /disclosures/{14자리 접수번호}` |
| SEC 공시 목록 | US | `GET /us-filings?symbol=AAPL&limit=2` |
| 이미 공개된 AI 공시 분석 | KR, US | `GET /disclosures/{id}/analysis` |
| 실적 발표 일정 | US | `GET /earnings` |
| IR·IPO 일정 | KR | `GET /ir-calendar`, `/ipo-offerings`, `/ipo-listings` |
| 경제 일정·공시 기반 기업 행사 | 지원 시장별 | `GET /economic-calendar`, `/events`, `/corporate-actions` |
| 지분·임원 거래·배당·자사주·종업원 | KR | `GET /major-holders/{symbol}`, `/insider-trades/{symbol}`, `/dividends/{symbol}`, `/treasury/{symbol}`, `/employees/{symbol}` |

기업별 가용 기간·필드가 다릅니다. 공시 목록에 있다는 이유만으로 모든 공시에 AI 분석이 존재하는 것은 아닙니다. 한국 원문과 미국 공시 목록은 별도 엔드포인트이며, `GET /disclosures`에는 한국 `symbol`이 필요합니다. `/symbols`는 한국 종목 검색입니다.

### 스크리너·섹터

간단한 조회는 전용 엔드포인트를 사용하세요.

```text
GET /screener?market=US&limit=10
GET /screener?market=KR&per_max=15&roe_min=10&limit=10
GET /sectors?market=US&metric=PER&limit=10
```

`/sectors`는 업종별 비교를 반환하며 `sector`를 지정하면 해당 업종의 종목 순위를 반환합니다. `metric` 기본값은 `PER`입니다. 두 경로는 기존 쿼리 엔진과 같은 데이터를 사용하며, 응답의 `results[0].ok`와 `status`를 확인한 뒤 `results[0].data`를 읽습니다. `limit`은 상위 개수(1~30)이며 커서 페이지네이션이 아닙니다. 기업 한 곳의 업종은 기존 `POST /query`의 `sector` 데이터셋으로 조회합니다.

경제 **일정**(`/economic-calendar`)은 제공하지만, 경제 **지표 시계열**(`/macro/*`)과 외부 컨센서스·애널리스트 리서치는 제공하지 않습니다.

Builder의 `POST /query`는 요청당 **쿼리 1개만** 받습니다. `market`과 `limit`은 아래처럼 쿼리 객체에 명시하세요.

```json
{"queries":[{"dataset":"screener","market":"US","limit":10}]}
```

허용된 쿼리 데이터셋은 `financials`, `metrics`, `segments`, `restatements`, `sector`, `sector_ranking`, `screener`, `dividends`, `financial_health`, `quote`입니다. **`quote`는 KR만** 가능합니다. 데이터셋별 입력 조건·지원 시장이 다르므로 명세를 확인하세요. HTTP 200이더라도 `results` 각 항목의 `ok`, `status`, `error`를 확인해야 합니다.

스크리너·섹터 결과에 포함된 가격·시가총액·밸류에이션은 프로젝트에서 활용할 수 있습니다. 미국 시세 엔드포인트나 가격 이력·스트리밍의 직접 호출은 제공하지 않습니다.

### 새 프리셋과 커스텀 조건

한국 28종·미국 27종을 `GET /screener`, `POST /query`, DATA MCP에서 동일하게 사용할 수 있습니다. `exchange-warning`(거래소 경고등)은 한국 전용입니다. 지원 프리셋 전체와 필터는 [DATA API 명세](https://api.chickstockfi.com/openapi/v1/openapi.json)의 `/screener`를 확인하세요.

| 프리셋 | 이름 | 시장 |
|---|---|---|
| `near-high` | 신고가 문턱 | KR·US |
| `volume-wake` | 거래량이 깬 종목 | KR·US |
| `growth-pullback` | 실적은 전진, 주가는 후진 | KR·US |
| `dividend-growth` | 배당도 성장도 놓치기 싫어 | KR·US |
| `profit-surge` | 이익에 가속 붙은 기업 | KR·US |
| `enemy-list` | 웬수에게도 추천 안 함 | KR·US |
| `loss-streak` | 3년째 적자 야근 | KR·US |
| `exchange-warning` | 거래소 경고등 | KR |

```text
GET /screener?market=KR&preset=enemy-list&limit=10
GET /screener?market=US&preset=near-high&limit=10
GET /screener?market=US&per_max=20&roe_min=10&market_cap_max=5000&rsi_min=40&rsi_max=70&sort=roe&order=desc&limit=10
```

시가총액 단위는 한국 **억원**, 미국 **백만 달러**입니다. 위 미국 예시의 `market_cap_max=5000`은 50억 달러입니다. RSI는 0~100, 52주 고점 대비 비율은 -100~0 범위이며 기술 지표는 확정 일봉 기준입니다. 분봉·실시간 매매 신호가 아닙니다.

`preset`과 직접 조건을 함께 보내면 직접 조건이 해당 프리셋 값을 덮어씁니다. 응답의 `appliedFilters`가 실제 적용 조건이고, 직접 조건으로 프리셋 설정을 바꾸면 `presetModified=true`입니다. 미지원 필드·없는 프리셋·역전된 범위는 오류로 반환됩니다. HTTP 상태뿐 아니라 GET·POST 모두 `results[i].ok/status/error`까지 확인하세요.

위험 스크리너에서는 `rows[].riskEvidence.codes`, `fiscalYear`, `asOf`와 `finRisk`를 함께 표시하세요. 재무 위험·거래소 지정에 대한 기록이며, 상장폐지를 예측하거나 확정하는 목록이 아닙니다. 결과가 `not_ready`이면 빈 목록으로 표시하지 말고 준비 중 상태를 안내하세요.

### 공매도

`GET /companies/005930/short-selling?series=volume&limit=5`처럼 조회합니다. 미국 종목은 `AAPL` 등 티커를 사용하세요. DATA MCP 도구는 `get_short_selling`입니다.

- `volume`: 일별 공매도 거래. 한국의 비중은 **거래대금 기준**, 미국은 **보고된 장외 거래량 기준**입니다. 미국 전체 시장의 거래량 비중이 아닙니다.
- `balance`: 한국의 보고된 순보유 공매도 잔고, 미국의 보고된 short interest입니다. 대차잔고와 구분하고 일별 거래량을 더해 잔고로 해석하지 마세요.
- `data[].date`는 관측일·정산일, `updated_at`은 저장 갱신 시각, `meta.as_of`는 응답 구성 시각입니다. **최신 응답이 최신 관측값을 뜻하지 않습니다.** 특히 미국 잔고는 종목별 범위와 저장된 기준일을 확인하세요.
- 수량은 주, 한국 금액은 원, 비율은 %입니다. 관측값 없음은 빈 배열(`meta.status=not_available`), 미확보 수치는 `null`이며 0이 아닙니다.
- `from`·`to`는 포함 경계입니다. 기본 50개·최대 200개, 날짜 최신순으로 `next_cursor`를 이어 사용합니다. 저장된 데이터만 읽고 새 수집·시세 조회·AI 생성을 실행하지 않습니다.

### 이미 공개된 분석

- 한국: 14자리 DART 접수번호. 미국: SEC 공시 목록의 `TICKER:ACCESSION` ID.
- `GET /disclosures/{id}/analysis`로 공개 기준을 충족한 저장 분석만 조회합니다. ID는 URL 인코딩하세요.
- 미국 목록에 `analysis=published`를 지정하면 공개 분석이 있는 공시를 찾을 수 있습니다.
- 없거나 공개 대상이 아닌 분석은 `404 ANALYSIS_NOT_AVAILABLE`입니다. 새 분석·번역을 생성하거나 갱신하지 않습니다.
- 기업 공시 목록의 `include_summary=true` 대신 위 분석 경로를 사용하세요. PRO 뉴스룸 기사와는 별도입니다.

## 제외 데이터·기능

| 제외 항목 | 안내 |
| --- | --- |
| PRO 전체 | PRO 웹·뉴스룸·PRO API·PRO MCP·개인 API 키·OAuth |
| 미국·일본 시세 직접 조회 | 현재가·가격 이력·스트리밍. 일본 시장 데이터도 이번 행사 범위에 포함되지 않습니다. |
| 뉴스·뉴스와이어 | `/news`는 첫 호출 예제로 사용하지 마세요. |
| 신규 AI 처리 | 분석·번역·기사 생성, 캐시 미스 시 생성, 강제 갱신 |
| 외부 컨센서스·애널리스트 리서치 | 일반 명세에 있어도 Builder에 포함되지 않습니다. |
| 웹훅 | 등록·관리·이벤트 전달 모두 미제공. 허용 한도 안에서 필요한 데이터만 조회하세요. |
| 글로벌 임상시험 | DATA API에서 제공 종료·deprecated 처리되었습니다. Builder 범위에도 포함되지 않습니다. |

## 기간과 한도

모든 시각은 **KST (UTC+09:00)**입니다.

| 단계 | 기간 | 팀별 총량 | 팀별 분당 한도 |
| --- | --- | ---: | ---: |
| 사전 테스트 | 활성화 후 ~ 2026-11-07 00:00 전 | 10,000회 | 60회 |
| 행사 | 2026-11-07 00:00 ~ 2026-11-08 00:00 전 | 50,000회 | 120회 |

- 최대 2개의 활성 DATA 키가 같은 팀 한도를 공유합니다. REST·MCP·API 문서 시험 호출도 함께 계산합니다.
- 단계별 총량입니다. 일일 리셋이 아니며, 키를 새로 만들어도 복구되지 않습니다. 행사 시작 시 별도의 50,000회가 적용됩니다.
- 팀별 동시 요청은 최대 4개입니다. 전체 행사 혼잡 제한도 적용될 수 있습니다.
- `GET /key`, MCP 초기화·`tools/list`는 DATA 조회 총량을 사용하지 않습니다. 메타데이터 호출에도 별도 속도 제한이 있습니다.
- 권한·시장 검사에서 거절된 요청은 조회 총량에 포함되지 않습니다. 검사 후 처리한 요청은 **400·404여도 집계될 수 있습니다.**
- `X-Quota-*` 헤더는 Builder에서 현재 **단계**의 한도·잔여량·종료 시각을 나타냅니다.
- 종료 후에는 이용이 자동 중지되며 무료 플랜으로 전환되지 않습니다. 연장이 필요하면 별도로 문의하세요.

## 외부 LLM·코드·데모

허용된 데이터를 행사 프로젝트의 외부 LLM 입력이나 MCP 도구 결과로 사용할 수 있습니다. 이는 Phoenix AI 서버에서 새 AI 결과를 생성하는 권한과 별개입니다.

프로젝트 코드와 결과 화면 데모를 공개할 수 있으며, 데이터 출처를 **Phoenix AI**로 표시해 주세요. 키·비밀번호·세션과 원본 응답 전체·데이터 덤프·재배포용 데이터셋은 공개 저장소에 넣지 마세요. 예제 코드 사용과 API 데이터 이용 권한은 구분됩니다.

행사 후 서비스 운영·계속 조회·데이터 재배포는 [도입 문의](https://openapi.chickstockfi.com/request)로 협의해 주세요. [서비스 이용약관](https://openapi.chickstockfi.com/terms)이 함께 적용됩니다.
