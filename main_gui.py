"""
빗썸 거래 프로그램 - GUI 버전
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from service import (
    get_markets, 
    market_order, 
    limit_order, 
    get_current_price, 
    get_my_balance
)
import json


class TradingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("빗썸 쌀먹 프로그램")
        self.root.geometry("600x750")
        self.root.resizable(False, False)
        
        # API 키 체크
        if not self.check_api_keys():
            self.show_api_key_dialog()
        
        self.markets = {}
        self.all_coins = []
        self.create_widgets()
        self.load_markets()
    
    def check_api_keys(self):
        """API 키 확인"""
        if not os.path.exists('.env'):
            return False
        
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        access_key = os.getenv("ACCESS_KEY")
        secret_key = os.getenv("SECRET_KEY")
        
        return bool(access_key and secret_key)
    
    def show_api_key_dialog(self):
        """API 키 입력 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        dialog.title("API 키 설정")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="API 키를 입력하세요", font=('', 12, 'bold')).pack(pady=10)
        
        tk.Label(dialog, text="Access Key:").pack(anchor='w', padx=20)
        access_entry = tk.Entry(dialog, width=50)
        access_entry.pack(padx=20, pady=5)
        
        tk.Label(dialog, text="Secret Key:").pack(anchor='w', padx=20)
        secret_entry = tk.Entry(dialog, width=50, show="*")
        secret_entry.pack(padx=20, pady=5)
        
        def save_keys():
            access_key = access_entry.get().strip()
            secret_key = secret_entry.get().strip()
            
            if not access_key or not secret_key:
                messagebox.showerror("오류", "API 키를 입력하세요")
                return
            
            try:
                with open('.env', 'w', encoding='utf-8') as f:
                    f.write(f"ACCESS_KEY={access_key}\n")
                    f.write(f"SECRET_KEY={secret_key}\n")
                
                messagebox.showinfo("성공", "API 키가 저장되었습니다")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("오류", f"저장 실패: {e}")
        
        tk.Button(dialog, text="저장", command=save_keys, bg='#4CAF50', fg='white', 
                 font=('', 10, 'bold'), padx=20, pady=5).pack(pady=20)
        
        dialog.wait_window()
    
    def create_widgets(self):
        """UI 구성"""
        # 타이틀
        title_frame = tk.Frame(self.root, bg='#2196F3', height=60)
        title_frame.pack(fill='x')
        tk.Label(title_frame, text="빗썸 쌀먹 프로그램", font=('', 16, 'bold'), 
                bg='#2196F3', fg='white').pack(pady=15)
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # 코인 검색
        tk.Label(main_frame, text="코인 검색", font=('', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        self.search_entry = tk.Entry(main_frame, textvariable=self.search_var, width=30, font=('', 11))
        self.search_entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5)
        
        # 검색 결과 리스트
        self.coin_listbox = tk.Listbox(main_frame, height=6, font=('', 10))
        self.coin_listbox.grid(row=1, column=1, columnspan=2, sticky='ew', pady=5)
        self.coin_listbox.bind('<<ListboxSelect>>', self.on_coin_selected)
        
        # 스크롤바
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=self.coin_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky='ns', pady=5)
        self.coin_listbox.config(yscrollcommand=scrollbar.set)
        
        # 현재가
        tk.Label(main_frame, text="현재가", font=('', 11, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.price_label = tk.Label(main_frame, text="-", font=('', 11), fg='#FF5722')
        self.price_label.grid(row=2, column=1, sticky='w', pady=5)
        
        # 주문 종류
        tk.Label(main_frame, text="주문 종류", font=('', 11, 'bold')).grid(row=3, column=0, sticky='w', pady=10)
        self.side_var = tk.StringVar(value='bid')
        tk.Radiobutton(main_frame, text="매수", variable=self.side_var, value='bid').grid(row=3, column=1, sticky='w')
        tk.Radiobutton(main_frame, text="매도", variable=self.side_var, value='ask').grid(row=3, column=2, sticky='w')
        
        # 주문 타입
        tk.Label(main_frame, text="주문 타입", font=('', 11, 'bold')).grid(row=4, column=0, sticky='w', pady=10)
        self.order_type_var = tk.StringVar(value='price')
        tk.Radiobutton(main_frame, text="시장가 매수", variable=self.order_type_var, 
                      value='price', command=self.on_order_type_changed).grid(row=4, column=1, sticky='w')
        tk.Radiobutton(main_frame, text="시장가 매도", variable=self.order_type_var, 
                      value='market', command=self.on_order_type_changed).grid(row=4, column=2, sticky='w')
        tk.Radiobutton(main_frame, text="지정가", variable=self.order_type_var, 
                      value='limit', command=self.on_order_type_changed).grid(row=5, column=1, sticky='w')
        
        # 금액/수량 입력
        tk.Label(main_frame, text="금액/수량", font=('', 11, 'bold')).grid(row=6, column=0, sticky='w', pady=10)
        self.amount_entry = tk.Entry(main_frame, width=20, font=('', 11))
        self.amount_entry.grid(row=6, column=1, sticky='ew', pady=10)
        self.amount_label = tk.Label(main_frame, text="(원)", font=('', 10))
        self.amount_label.grid(row=6, column=2, sticky='w')
        
        # 가격 입력 (지정가용)
        self.price_label_text = tk.Label(main_frame, text="가격", font=('', 11, 'bold'))
        self.price_label_text.grid(row=7, column=0, sticky='w', pady=10)
        self.price_entry = tk.Entry(main_frame, width=20, font=('', 11))
        self.price_entry.grid(row=7, column=1, sticky='ew', pady=10)
        self.price_unit_label = tk.Label(main_frame, text="(원)", font=('', 10))
        self.price_unit_label.grid(row=7, column=2, sticky='w')
        
        # 초기에는 가격 입력 숨김
        self.price_label_text.grid_remove()
        self.price_entry.grid_remove()
        self.price_unit_label.grid_remove()
        
        # 버튼
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=20)
        
        tk.Button(button_frame, text="주문하기", command=self.place_order, 
                 bg='#4CAF50', fg='white', font=('', 12, 'bold'), 
                 padx=30, pady=10).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="잔고확인", command=self.check_balance, 
                 bg='#2196F3', fg='white', font=('', 12, 'bold'), 
                 padx=30, pady=10).pack(side='left', padx=5)
        
        # 결과 표시
        tk.Label(main_frame, text="결과", font=('', 11, 'bold')).grid(row=9, column=0, sticky='nw', pady=5)
        self.result_text = scrolledtext.ScrolledText(main_frame, height=8, width=50, font=('Consolas', 9))
        self.result_text.grid(row=9, column=1, columnspan=2, sticky='ew', pady=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def on_order_type_changed(self):
        """주문 타입 변경 시"""
        order_type = self.order_type_var.get()
        
        if order_type == 'price':
            self.amount_label.config(text="(원)")
            self.price_label_text.grid_remove()
            self.price_entry.grid_remove()
            self.price_unit_label.grid_remove()
        elif order_type == 'market':
            self.amount_label.config(text="(전액 매도)")
            self.amount_entry.config(state='disabled')
            self.price_label_text.grid_remove()
            self.price_entry.grid_remove()
            self.price_unit_label.grid_remove()
        else:  # limit
            self.amount_label.config(text="(수량)")
            self.amount_entry.config(state='normal')
            self.price_label_text.grid()
            self.price_entry.grid()
            self.price_unit_label.grid()
    
    def load_markets(self):
        """마켓 정보 로드"""
        self.log("마켓 정보 로딩중...")
        try:
            self.markets = get_markets()
            if self.markets:
                self.all_coins = sorted(list(self.markets.keys()))
                self.update_coin_list(self.all_coins)
                self.log(f"총 {len(self.markets)}개 코인 로드 완료")
            else:
                self.log("마켓 정보 로드 실패")
        except Exception as e:
            self.log(f"오류: {e}")
    
    def on_search_changed(self, *args):
        """검색어 변경 시 리스트 업데이트"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # 검색어가 없으면 전체 표시
            filtered = self.all_coins
        else:
            # 검색어로 필터링
            filtered = [coin for coin in self.all_coins if search_term in coin.lower()]
        
        self.update_coin_list(filtered)
    
    def update_coin_list(self, coins):
        """코인 리스트 업데이트"""
        self.coin_listbox.delete(0, tk.END)
        for coin in coins:
            self.coin_listbox.insert(tk.END, coin)
    
    def on_coin_selected(self, event):
        """코인 선택 시 현재가 조회"""
        selection = self.coin_listbox.curselection()
        if not selection:
            return
        
        coin_name = self.coin_listbox.get(selection[0])
        if not coin_name or coin_name not in self.markets:
            return
        
        market_code = self.markets[coin_name]
        try:
            current_price = get_current_price(market_code)
            if current_price:
                self.price_label.config(text=f"{current_price:,.0f}원")
                self.log(f"{coin_name} 선택: {current_price:,.0f}원")
            else:
                self.price_label.config(text="조회 실패")
        except Exception as e:
            self.log(f"현재가 조회 오류: {e}")
    
    def place_order(self):
        """주문 실행"""
        selection = self.coin_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "코인을 선택하세요")
            return
        
        coin_name = self.coin_listbox.get(selection[0])
        
        market_code = self.markets[coin_name]
        side = self.side_var.get()
        order_type = self.order_type_var.get()
        
        try:
            if order_type == 'price':
                price = float(self.amount_entry.get())
                self.log(f"시장가 매수: {price:,.0f}원")
                result = market_order(market_code, side, 'price', price=price)
                
            elif order_type == 'market':
                # 잔고 조회
                balances = get_my_balance()
                ticker = market_code.split('-')[1]
                volume = 0
                for asset in balances:
                    if asset.get('currency') == ticker:
                        volume = float(asset.get('balance', 0))
                        break
                
                if volume == 0:
                    messagebox.showwarning("경고", f"{coin_name} 잔고가 없습니다")
                    return
                
                self.log(f"시장가 매도: {volume} {ticker}")
                result = market_order(market_code, side, 'market', volume=volume)
                
            else:  # limit
                volume = float(self.amount_entry.get())
                price = float(self.price_entry.get())
                self.log(f"지정가 주문: {volume} @ {price:,.0f}원")
                result = limit_order(market_code, side, volume, price)
            
            self.log(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('uuid'):
                messagebox.showinfo("성공", "주문이 완료되었습니다")
            else:
                messagebox.showerror("실패", result.get('error', {}).get('message', '주문 실패'))
                
        except ValueError:
            messagebox.showerror("오류", "금액/수량을 올바르게 입력하세요")
        except Exception as e:
            self.log(f"주문 오류: {e}")
            messagebox.showerror("오류", str(e))
    
    def check_balance(self):
        """잔고 확인"""
        try:
            balances = get_my_balance()
            self.result_text.delete('1.0', tk.END)
            self.log("=== 잔고 ===")
            for asset in balances:
                balance = float(asset.get('balance', 0))
                if balance > 0:
                    currency = asset.get('currency')
                    self.log(f"{currency}: {balance}")
        except Exception as e:
            self.log(f"잔고 조회 오류: {e}")
    
    def log(self, message):
        """로그 출력"""
        self.result_text.insert(tk.END, message + '\n')
        self.result_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = TradingGUI(root)
    root.mainloop()

