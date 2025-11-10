# Bithumb Trading Automation

빗썸 거래소 API를 활용한 자동 매매 프로그램. GUI/CLI 인터페이스 지원 및 단일 실행 파일 배포.

## Features

- **주문 타입 지원**: 시장가/지정가 매수/매도
- **자동 잔고 조회**: 전액 매도 시 잔고 자동 계산
- **실시간 시세**: WebSocket 기반 실시간 가격 조회
- **GUI/CLI 인터페이스**: tkinter 기반 GUI 및 터미널 CLI
- **단일 실행 파일**: PyInstaller로 빌드된 standalone EXE
- **JWT 인증**: 빗썸 API JWT 토큰 자동 생성

## Installation

### For End Users

**실행 파일 다운로드 (Python 불필요)**

[Releases](https://github.com/Akisigure/bithumb_ssalmuk/releases)에서 최신 버전의 `BithumbGUI.exe`를 다운로드하여 바로 실행.

### For Developers

**Requirements:**
- Python 3.10+
- Dependencies: `python-dotenv`, `PyJWT`, `requests`

**Setup:**

```bash
git clone https://github.com/Akisigure/bithumb_ssalmuk.git
cd bithumb_ssalmuk

# 의존성 설치
uv sync
# or
pip install python-dotenv PyJWT requests

# 실행
python main_gui.py  # GUI 버전
python main.py      # CLI 버전
```

**빌드:**

```bash
# GUI 버전
build_gui.bat

# CLI 버전
build.bat

# 출력
dist/BithumbGUI.exe
```

## Configuration

첫 실행 시 빗썸 API 키 입력 프롬프트가 표시되며, 입력된 키는 `.env` 파일에 자동 저장됨.

```
Access Key를 입력하세요: <your-access-key>
Secret Key를 입력하세요: <your-secret-key>
```

`.env` 파일 생성 후 재입력 불필요. API 키 재설정 시 `.env` 파일 삭제 후 재실행.

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

## Build

PyInstaller를 사용한 단일 실행 파일 빌드.

```bash
# GUI 버전 (권장)
build_gui.bat
# Output: dist/BithumbGUI.exe

# CLI 버전
build.bat
# Output: dist/빗썸거래.exe

# Manual build
python build_exe.py
pyinstaller --onefile --console --name=빗썸거래 --clean main.py
```

빌드 결과물은 `dist/` 디렉토리에 생성됨 (약 15-20MB).

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
├── main_gui.py       # GUI 인터페이스
├── main.py           # CLI 인터페이스
├── service.py        # Bithumb API wrapper
├── utils.py          # JWT 인증 헬퍼
├── build_gui.bat     # GUI 빌드 스크립트
├── build.bat         # CLI 빌드 스크립트
├── build_exe.py      # PyInstaller 설정
├── .env              # API 키 (자동 생성)
└── dist/             # 빌드 출력 디렉토리
    └── BithumbGUI.exe
```

## Troubleshooting

### API 인증 실패
`.env` 파일 삭제 후 재실행하여 API 키 재입력:
```bash
rm .env
python main.py  # 또는 BithumbGUI.exe
```

### 주문 실패
- 최소 주문 금액: 5,000 KRW (권장: 5,500 KRW 이상)
- 수량 소숫점: 최대 8자리까지 지원

### API 키 재설정
```bash
rm .env && python main.py
```

## Distribution

빌드된 `BithumbGUI.exe`는 단일 실행 파일로 배포 가능. Python 런타임이 내장되어 있어 별도 설치 불필요.

**배포 방법:**
1. GitHub Releases에 업로드 (권장)
2. 직접 전달

사용자는 첫 실행 시 API 키만 입력하면 즉시 사용 가능.

## Disclaimer

실제 거래로 인한 손실에 대해 개발자는 책임지지 않음. 투자는 본인 책임.
