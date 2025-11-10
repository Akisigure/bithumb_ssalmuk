"""
빗썸 거래소 자동 매매 프로그램
"""
import os
from service import (
    get_markets, 
    market_order, 
    limit_order, 
    get_current_price, 
    get_my_balance
)
from pprint import pprint


def setup_api_keys():
    """
    API 키 설정 - .env 파일 생성
    """
    print("\n" + "=" * 60)
    print("🔑 API 키 설정")
    print("=" * 60)
    print("\n⚠️  API 키는 안전하게 .env 파일에 저장됩니다.")
    print("⚠️  이 파일은 다른 사람과 공유하지 마세요!\n")
    
    access_key = input("Access Key를 입력하세요: ").strip()
    secret_key = input("Secret Key를 입력하세요: ").strip()
    
    if not access_key or not secret_key:
        print("\n❌ API 키를 입력하지 않았습니다.")
        return False
    
    # .env 파일 생성
    env_content = f"""# 빗썸 API 설정
ACCESS_KEY={access_key}
SECRET_KEY={secret_key}

# 이 파일은 자동으로 생성되었습니다.
# API 키는 절대 다른 사람과 공유하지 마세요!
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n✅ API 키가 성공적으로 저장되었습니다!")
        print("💾 저장 위치: .env 파일\n")
        return True
    except Exception as e:
        print(f"\n❌ .env 파일 저장 실패: {e}")
        return False


def check_api_keys():
    """
    API 키 설정 확인
    - .env 파일이 있으면 스킵
    - .env 파일이 없으면 API 키 입력 요청
    """
    # .env 파일 존재 확인
    if not os.path.exists('.env'):
        print("\n⚠️  API 키가 설정되어 있지 않습니다.")
        print("📝 처음 사용하시는군요! API 키를 설정해주세요.\n")
        return setup_api_keys()
    
    # 환경 변수 로드
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    access_key = os.getenv("ACCESS_KEY")
    secret_key = os.getenv("SECRET_KEY")
    
    # API 키 유효성 확인
    if not access_key or not secret_key:
        print("\n⚠️  .env 파일이 있지만 API 키가 올바르지 않습니다.")
        print("🔧 API 키를 다시 설정합니다.\n")
        return setup_api_keys()
    
    # API 키가 정상적으로 로드됨
    print("\n✅ API 키 확인 완료")
    return True


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("빗썸 자동 거래 프로그램")
    print("=" * 60)
    
    # API 키 확인
    if not check_api_keys():
        print("\n❌ API 키 설정에 실패했습니다. 프로그램을 종료합니다.")
        input("\nEnter를 눌러 종료...")
        return
    
    # 마켓 정보 로드
    markets = get_markets()
    if not markets:
        print("❌ 마켓 정보를 불러오는데 실패했습니다.")
        return
    
    print(f"\n✅ 총 {len(markets)}개 코인 거래 가능")
    
    # 코인 선택
    market_name = input("\n코인 이름을 입력하세요 (예: 비트코인): ").strip()
    
    if market_name not in markets:
        print(f"❌ '{market_name}'은(는) 거래 가능한 코인이 아닙니다.")
        print(f"💡 사용 가능한 코인 리스트: {', '.join(list(markets.keys())[:10])}...")
        return
    
    market_code = markets[market_name]
    ticker = market_code.split('-')[1]
    
    # 현재가 조회
    current_price = get_current_price(market_code)
    if current_price:
        print(f"\n📊 {market_name} 현재가: {current_price:,.0f}원")
    else:
        print(f"❌ 현재가 조회 실패")
        return
    
    # 주문 종류 선택
    print("\n" + "=" * 60)
    print("주문 종류를 선택하세요")
    print("=" * 60)
    print("1. 매수 (bid)")
    print("2. 매도 (ask)")
    
    side_choice = input("\n선택 (1/2): ").strip()
    side = 'bid' if side_choice == '1' else 'ask' if side_choice == '2' else None
    
    if not side:
        print("❌ 잘못된 선택입니다.")
        return
    
    # 주문 타입 선택
    print("\n" + "=" * 60)
    print("주문 타입을 선택하세요")
    print("=" * 60)
    print("1. 시장가 매수 (price) - 원화 금액 입력")
    print("2. 시장가 매도 (market) - 전액 매도")
    print("3. 지정가 주문 (limit) - 수량/가격 지정")
    
    order_choice = input("\n선택 (1/2/3): ").strip()
    
    # 시장가 매수
    if order_choice == '1':
        if side != 'bid':
            print("❌ 시장가 매수는 매수(bid)만 가능합니다.")
            return
        
        price = float(input("\n매수할 금액을 입력하세요 (원): "))
        print(f"\n💰 주문 정보: {market_name} {price:,.0f}원 시장가 매수")
        
        confirm = input("주문을 실행하시겠습니까? (y/n): ").strip().lower()
        if confirm == 'y':
            result = market_order(market_code, side, 'price', price=price)
            print("\n📋 주문 결과:")
            pprint(result)
    
    # 시장가 매도 (전액)
    elif order_choice == '2':
        if side != 'ask':
            print("❌ 시장가 매도는 매도(ask)만 가능합니다.")
            return
        
        # 잔고 조회
        balances = get_my_balance()
        volume = 0
        
        for asset in balances:
            if asset.get('currency') == ticker:
                volume = float(asset.get('balance', 0))
                break
        
        if volume == 0:
            print(f"❌ 보유한 {market_name}이(가) 없습니다.")
            return
        
        print(f"\n💰 보유 수량: {volume} {ticker}")
        print(f"💰 예상 금액: {volume * current_price:,.0f}원")
        
        confirm = input("전액 매도하시겠습니까? (y/n): ").strip().lower()
        if confirm == 'y':
            result = market_order(market_code, side, 'market', volume=volume)
            print("\n📋 주문 결과:")
            pprint(result)
    
    # 지정가 주문
    elif order_choice == '3':
        volume = float(input("\n주문 수량을 입력하세요: "))
        price = float(input("주문 가격을 입력하세요 (1개당 원): "))
        
        volume = round(volume, 8)
        total = volume * price
        
        side_str = "매수" if side == 'bid' else "매도"
        print(f"\n💰 주문 정보: {market_name} {volume} {ticker} @ {price:,.0f}원 지정가 {side_str}")
        print(f"💰 총 금액: {total:,.0f}원")
        
        confirm = input("주문을 실행하시겠습니까? (y/n): ").strip().lower()
        if confirm == 'y':
            result = limit_order(market_code, side, volume, price)
            print("\n📋 주문 결과:")
            pprint(result)
    
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    print("\n" + "=" * 60)
    print("거래가 완료되었습니다.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
