from dotenv import load_dotenv
import os
from utils import get_param_jwt
import requests
import json
from collections import defaultdict

API_URL = "https://api.bithumb.com"


def get_api_keys():
    """
    API 키를 동적으로 로드
    .env 파일이 변경되어도 재시작 없이 바로 반영됨
    """
    load_dotenv(override=True)  # 매번 최신 값으로 로드
    return os.getenv("ACCESS_KEY"), os.getenv("SECRET_KEY")


# ==================== 주문 API ====================

def market_order(market, side, ord_type, price=None, volume=None):
    """
    시장가 매수/매도 주문
    
    Args:
        market (str): 마켓 ID (예: 'KRW-BTC')
        side (str): 주문 종류 ('bid': 매수, 'ask': 매도)
        ord_type (str): 주문 타입 ('price': 시장가 매수, 'market': 시장가 매도)
        price (float, optional): 매수할 금액 (KRW) - ord_type='price'일 때 필수
        volume (float, optional): 매도할 수량 - ord_type='market'일 때 필수
    
    Returns:
        dict: API 응답 결과
    """
    # 시장가 매수: ord_type='price', price만 전송
    if ord_type == 'price':
        request_body = {
            'market': market,
            'side': side,
            'price': str(price),
            'ord_type': 'price'
        }
    # 시장가 매도: ord_type='market', volume만 전송
    elif ord_type == 'market':
        request_body = {
            'market': market,
            'side': side,
            'volume': str(volume),
            'ord_type': 'market'
        }
    else:
        return {'error': f'잘못된 ord_type: {ord_type}'}
    
    return _send_order(request_body)


def limit_order(market, side, volume, price):
    """
    지정가 주문
    
    Args:
        market (str): 마켓 ID (예: 'KRW-BTC')
        side (str): 주문 종류 ('bid': 매수, 'ask': 매도)
        volume (float): 주문 수량
        price (float): 주문 가격 (1개당 가격)
    
    Returns:
        dict: API 응답 결과
    """
    request_body = {
        'market': market,
        'side': side,
        'volume': str(volume),
        'price': str(price),
        'ord_type': 'limit'
    }
    
    return _send_order(request_body)


def _send_order(request_body):
    """
    주문 요청을 서버로 전송 (내부 함수)
    
    Args:
        request_body (dict): 주문 요청 바디
    
    Returns:
        dict: API 응답 결과
    """
    # API 키 동적 로드
    access_key, secret_key = get_api_keys()
    
    if not access_key or not secret_key:
        return {'error': 'API 키가 설정되지 않았습니다. 설정에서 API 키를 입력하세요.'}
    
    # JWT 토큰 생성
    authorization_token = get_param_jwt(access_key, secret_key, request_body)
    
    headers = {
        'Authorization': authorization_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            API_URL + '/v1/orders',
            data=json.dumps(request_body),
            headers=headers
        )
        return response.json()
    except Exception as e:
        return {'error': str(e)}


# ==================== 조회 API ====================

def get_my_balance():
    """
    내 계좌 잔고 조회
    
    Returns:
        list: 보유 자산 리스트
            [{
                'currency': 'KRW',
                'balance': '1000000',
                'locked': '0',
                'avg_buy_price': '0',
                ...
            }, ...]
    """
    # API 키 동적 로드
    access_key, secret_key = get_api_keys()
    
    if not access_key or not secret_key:
        return [{'error': 'API 키가 설정되지 않았습니다. 설정에서 API 키를 입력하세요.'}]
    
    authorization_token = get_param_jwt(access_key, secret_key, {})
    
    headers = {
        'Authorization': authorization_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{API_URL}/v1/accounts', headers=headers)
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def get_current_price(market):
    """
    현재가 조회
    
    Args:
        market (str): 마켓 ID (예: 'KRW-BTC')
    
    Returns:
        float: 현재 거래가
    """
    headers = {"accept": "application/json"}
    
    try:
        response = requests.get(
            f'{API_URL}/v1/ticker',
            headers=headers,
            params={'markets': market}
        )
        return response.json()[0]['trade_price']
    except Exception as e:
        return None


def get_orderbook(market):
    """
    호가 정보 조회
    
    Args:
        market (str): 마켓 ID (예: 'KRW-BTC')
    
    Returns:
        dict: 호가 정보
    """
    headers = {"accept": "application/json"}
    
    try:
        response = requests.get(
            f'{API_URL}/v1/orderbook',
            headers=headers,
            params={'markets': market}
        )
        return response.json()
    except Exception as e:
        return {'error': str(e)}


def get_markets():
    """
    전체 마켓 코드 조회
    
    Returns:
        dict: {한글명: 마켓코드} 형태의 딕셔너리
            {'비트코인': 'KRW-BTC', '이더리움': 'KRW-ETH', ...}
    """
    headers = {"accept": "application/json"}
    
    try:
        response = requests.get(f'{API_URL}/v1/market/all', headers=headers)
        markets = defaultdict(str)
        
        for item in response.json():
            # 중복된 한글명이 있으면 첫 번째만 사용
            if not markets.get(item['korean_name']):
                markets[item['korean_name']] = item['market']
        
        return dict(markets)
    except Exception as e:
        return {}
