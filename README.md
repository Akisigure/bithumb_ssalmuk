# 빗썸 쌀먹 프로그램

빗썸 API 10만원 이벤트용 프젝

## Features

- 시장가 매수/매도
- 지정가 주문
- 전액 매도 (잔고 자동 조회)
- 실시간 시세 조회
- 단일 EXE 배포 가능

## Requirements

- Python 3.10+
- Dependencies: `python-dotenv`, `PyJWT`, `requests`

## Quick Start

### GUI 버전 (추천) 🎨

```bash
# 빌드
build_gui.bat

# 실행
dist/BithumbGUI.exe
```

- 직관적인 GUI 인터페이스
- 코인 선택 드롭다운
- 실시간 현재가 표시
- 주문 결과 실시간 표시

### CLI 버전

```bash
# 빌드
build.bat

# 실행
dist/BithumbCLI.exe
```

### Python 사용 (개발자)

```bash
# Clone
git clone <repository-url>
cd bithumb

# Install
uv sync
# or
pip install python-dotenv PyJWT requests

# Run
python main_gui.py  # GUI 버전
python main.py      # CLI 버전
```

첫 실행 시 API 키 자동 입력:
```
Access Key를 입력하세요: <your-key>
Secret Key를 입력하세요: <your-secret>
```

API 키는 `.env`에 자동 저장되며, 이후 실행 시 입력 불필요

## Usage

### CLI 실행 흐름

1. 코인 선택 (예: 비트코인)
2. 주문 타입 선택
   - `1`: 매수
   - `2`: 매도
3. 거래 방식 선택
   - `1`: 시장가 매수 (금액 입력)
   - `2`: 시장가 매도 (전액)
   - `3`: 지정가 주문 (수량/가격 지정)
4. 주문 확인 및 실행

### Python API

```python
from service import market_order, limit_order, get_current_price, get_my_balance

# 시장가 매수: 10,000원어치
market_order('KRW-BTC', 'bid', 'price', price=10000)

# 시장가 매도: 0.001 BTC
market_order('KRW-BTC', 'ask', 'market', volume=0.001)

# 지정가 매수: 0.001 BTC @ 100,000,000원
limit_order('KRW-BTC', 'bid', 0.001, 100000000)

# 현재가
price = get_current_price('KRW-BTC')

# 잔고
balances = get_my_balance()
```

## Build EXE

```bash
# Windows 배치 파일
build.bat

# Python 스크립트
python build_exe.py

# PyInstaller 직접
pyinstaller --onefile --console --name=빗썸거래 --clean main.py
```

빌드 결과: `dist/빗썸거래.exe` (약 15-20MB)

## API Authentication

JWT 기반 인증 (HS256)

```python
payload = {
    'access_key': ACCESS_KEY,
    'nonce': str(uuid.uuid4()),
    'timestamp': round(time.time() * 1000),
    'query_hash': hashlib.sha512(query).hexdigest(),
    'query_hash_alg': 'SHA512'
}
jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

## Order Types

| Type | Params | Description |
|------|--------|-------------|
| `price` | `price` | 시장가 매수 (즉시 체결) |
| `market` | `volume` | 시장가 매도 (즉시 체결) |
| `limit` | `volume`, `price` | 지정가 주문 (호가창 등록) |

## Project Structure

```
bithumb/
├── main.py           # CLI 인터페이스
├── service.py        # API 함수
├── utils.py          # JWT 인증
├── build.bat         # Windows 빌드
├── build_exe.py      # 빌드 스크립트
└── .env              # API 키 (자동 생성)
```

## Troubleshooting

**API 인증 실패**
```bash
# .env 파일 삭제 후 재실행
rm .env
python main.py
```

**주문 실패**
- 최소 주문 금액: 5,000 KRW 넉넉히 5500 KRW 이상 권장
- 수량 소숫점: 최대 8자리

**API 키 재설정**
```bash
rm .env && python main.py
```

## Distribution

배포 시 `빗썸거래.exe` 파일만 전달
- 별도 설정 파일 불필요
- API 키는 실행 시 자동 입력

## Disclaimer

실제 거래로 인한 손실에 대해 개발자는 책임지지 않음. 투자는 본인 책임.
