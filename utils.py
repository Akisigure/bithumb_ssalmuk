import jwt 
import uuid
import time
from urllib.parse import urlencode
import hashlib


def get_param_jwt(api_key, api_secret, params):
    """
    파라미터가 있는 요청에 사용할 JWT 토큰 생성
    
    Args:
        api_key: 빗썸 Access Key
        api_secret: 빗썸 Secret Key
        params: 요청 파라미터 딕셔너리 (빈 딕셔너리 가능)
    
    Returns:
        Bearer JWT 토큰 문자열
    """
    # 파라미터를 URL 인코딩
    query = urlencode(params).encode()
    
    # SHA512 해시 생성
    hash_obj = hashlib.sha512()
    hash_obj.update(query)
    query_hash = hash_obj.hexdigest()
    
    # JWT 페이로드 생성
    payload = {
        'access_key': api_key,
        'nonce': str(uuid.uuid4()),
        'timestamp': round(time.time() * 1000), 
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }
    
    # JWT 토큰 생성 (HS256 알고리즘)
    jwt_token = jwt.encode(payload, api_secret, algorithm='HS256')
    authorization_token = f'Bearer {jwt_token}'
    
    return authorization_token
