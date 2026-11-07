# DATA MCP 연결

[처음으로](../README.md) · [제공 범위](coverage.md)

Builder는 `https://api.chickstockfi.com/openapi/v1/mcp`에 **DATA 키(`ck_live_…`)**로 연결합니다. PRO MCP 주소·`ck_pers_`·OAuth 로그인은 사용하지 않습니다. REST와 같은 계정·시장·한도·만료 조건이 적용됩니다.

## Claude Code

1. [README의 환경변수 설정](../README.md)을 마친 터미널을 사용합니다.
2. [`config/claude.mcp.json.example`](../config/claude.mcp.json.example)의 내용을 프로젝트 `.mcp.json`에 추가합니다. 이미 파일이 있다면 `mcpServers` 항목을 합치세요.
3. 같은 터미널에서 `claude`를 시작한 뒤 `/mcp`에서 `phoenix-data` 연결 상태를 확인합니다.

```json
{
  "mcpServers": {
    "phoenix-data": {
      "type": "http",
      "url": "https://api.chickstockfi.com/openapi/v1/mcp",
      "headers": { "Authorization": "Bearer ${PHOENIX_DATA_KEY}" }
    }
  }
}
```

`${PHOENIX_DATA_KEY}`는 Claude Code가 실행된 프로세스의 환경변수를 읽습니다. 설정 JSON에 실제 키를 적을 필요가 없습니다. [Claude Code 공식 MCP 설정 문서](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcpjson)를 참고하세요.

## Cursor

[`config/cursor.mcp.json.example`](../config/cursor.mcp.json.example)을 프로젝트 `.cursor/mcp.json` 또는 사용자 `~/.cursor/mcp.json`에 합칩니다.

```json
{
  "mcpServers": {
    "phoenix-data": {
      "url": "https://api.chickstockfi.com/openapi/v1/mcp",
      "headers": { "Authorization": "Bearer ${env:PHOENIX_DATA_KEY}" }
    }
  }
}
```

Cursor의 변수 표기는 `${env:PHOENIX_DATA_KEY}`입니다. 원격 HTTP MCP는 `.env` 파일을 자동으로 읽지 않습니다. Cursor를 완전히 종료한 뒤 키를 설정한 터미널에서 `cursor .`로 시작하거나, 사용 중인 OS의 안전한 환경변수 설정을 사용하세요. [Cursor 공식 설정 문서](https://cursor.com/docs/mcp#config-interpolation)를 참고하세요.

## 첫 질문

먼저 도구 목록을 확인하고 아래처럼 요청해 보세요. 모든 도구를 한꺼번에 실행하지 마세요.

> Phoenix DATA MCP의 get_api_usage로 현재 시장, 남은 호출 수, 만료 시각을 확인해 주세요.

> list_disclosures에 symbol="005930", limit=2를 넣어 최근 한국 공시를 보여 주세요. 분석은 새로 생성하지 마세요.

> run_data_query로 {"queries":[{"dataset":"screener","market":"US","limit":3}]}을 요청해 주세요. 데이터 기준 시각과 단위를 함께 표시해 주세요.

> get_short_selling에 symbol="005930", series="volume", limit=5를 넣어 공매도 거래 추이를 보여 주세요. 잔고와 구분하고 관측일·단위를 표시해 주세요.

`tools/list`에 실제 계정에서 사용할 수 있는 도구가 나옵니다. 예: `get_quote`(KR), `get_company_financials`, `list_us_filings`, `get_published_disclosure_analysis`, `get_earnings_calendar`. 도구 인자 스키마를 확인한 후 호출하세요.

MCP가 HTTP 200을 반환해도 JSON-RPC `error` 또는 도구 결과의 `isError: true`이면 성공이 아닙니다. 429·권한 거절·만료를 무시하고 반복 호출하지 마세요. [오류 처리](troubleshooting.md)를 참고하세요.

## 키 관리

- MCP 설정에는 변수 참조만 유지하고 실제 값은 환경변수에 둡니다.
- 팀원이 여러 도구를 연결해도 분당·총량 한도는 팀 단위로 공유합니다.
- 허용되지 않은 PRO·웹훅·새 AI 생성 도구를 다른 URL로 시도하지 마세요.
- 연결 문제를 문의할 때 키·Authorization 헤더·세션은 보내지 마세요.

스크리너와 섹터는 `get_screener`, `get_sector_rankings` 도구로도 바로 조회할 수 있습니다. `market`은 `KR` 또는 `US`, `limit`은 1~30입니다. 기존 `run_data_query`도 유지됩니다.

### 새 스크리너와 커스텀 조회

`get_screener`는 한국 28종·미국 27종과 커스텀 필터를 지원합니다. 예:

```json
{"market":"KR","preset":"enemy-list","limit":5}
```

```json
{"market":"US","per_max":20,"roe_min":10,"rsi_min":40,"rsi_max":70,"market_cap_max":5000,"sort":"roe","order":"desc","limit":5}
```

`exchange-warning`은 KR 전용입니다. `appliedFilters`와 지표 기준일, 위험 항목의 `riskEvidence`를 함께 설명하세요. 지원하지 않는 필드는 무시되지 않고 거절됩니다. 기존 `run_data_query`에서도 동일하게 사용할 수 있으며 Builder는 요청당 쿼리 한 개만 허용합니다.
