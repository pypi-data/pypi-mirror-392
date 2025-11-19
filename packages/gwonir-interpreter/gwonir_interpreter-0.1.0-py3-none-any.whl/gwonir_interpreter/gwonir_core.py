# gwonir_core.py (최종 안정화 버전)
import re
import sys
import random

VARS = {}
OUTPUT_BUFFER = ""

# --- 도우미 함수 ---

def resolve_value(token):
    """토큰(변수명, 숫자, 문자열)을 실제 값으로 해석합니다."""
    token = token.strip()
    # 1. 문자열 처리
    if token.startswith('"') and token.endswith('"'): return token.strip('"')
    # 2. 숫자 처리
    try: return float(token)
    except ValueError: pass
    # 3. 변수명 처리
    if token in VARS: return VARS[token]
    raise NameError(f"미정의 변수 또는 알 수 없는 값: {token}")

def substitute_vars(expression):
    """수식이나 조건문 내의 변수명을 VARS의 실제 값으로 대체합니다."""
    def replace_vars(match):
        var_name = match.group(0)
        if var_name in VARS:
            val = VARS[var_name]
            if isinstance(val, (int, float)): return str(val)
            return f"'{val}'"
        return var_name

    tokens = re.split(r'([+\-*/<>=!&| ])', expression)
    substituted_tokens = []
    for token in tokens:
        if not token.strip() and token != ' ': substituted_tokens.append(token); continue
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token.strip()):
            try:
                if token.strip() in VARS: substituted_tokens.append(replace_vars(re.match(r'[A-Za-z_][A-Za-z0-9_]*', token)))
                else: substituted_tokens.append(token)
            except Exception: substituted_tokens.append(token)
        else: substituted_tokens.append(token)

    return "".join(substituted_tokens)

# --- 명령어 실행 함수 ---

def execute_assignment(line):
    """변수 할당: '권일아 기억해! 변수명 = 값'"""
    if not line.startswith('권일아 기억해!'): return
    try:
        assignment_part = line.replace('권일아 기억해!', '', 1).strip()
        var_name, expression = assignment_part.split('=', 1)
        var_name = var_name.strip()
        expression = expression.strip()
        value = resolve_value(expression)
        VARS[var_name] = value
    except Exception as e: print(f"!!! 변수 할당 처리 오류: {line} -> {e}")

def execute_print(line):
    """출력: '권일아 말해라(값)' 또는 '권일아 말해라(값);'"""
    global OUTPUT_BUFFER
    match = re.match(r'권일아 말해라\((.*?)\)(;)?$', line.strip())
    if not match: return
    
    content = match.group(1).strip() 
    needs_continuation = bool(match.group(2)) # 세미콜론이 있다면 줄바꿈 없음

    try:
        value = resolve_value(content) if content else ""
        OUTPUT_BUFFER += str(value)
        if not needs_continuation:
            print(OUTPUT_BUFFER)
            OUTPUT_BUFFER = ""
    except Exception as e:
        OUTPUT_BUFFER = ""
        print(f"[ERROR] 출력 오류: {line} -> {e}")

def execute_calculation(line):
    """계산: '권일아 계산해! 수식 = 변수명'"""
    if not line.startswith('권일아 계산해!'): return
    try:
        calc_part = line.replace('권일아 계산해!', '', 1).strip()
        expression, result_var_name = calc_part.split('=', 1)
        result_var_name = result_var_name.strip()
        eval_expression = substitute_vars(expression)
        calculation_result = eval(eval_expression)
        VARS[result_var_name] = calculation_result
    except Exception as e: print(f"[ERROR] 계산 처리 오류: {line} -> {e}")

def execute_input(line):
    """입력: '권일아 니가 원하는거 함 골라봐라 [프롬프트] = [변수명]'"""
    if not line.startswith('권일아 니가 원하는거 함 골라봐라'): return
    try:
        input_part = line.replace('권일아 니가 원하는거 함 골라봐라', '', 1).strip()
        prompt_expression, result_var_name = input_part.split('=', 1)
        result_var_name = result_var_name.strip()
        prompt = resolve_value(prompt_expression)
        user_input_str = input(f"[궈니르 입력] {prompt}: ").strip()
        try: VARS[result_var_name] = float(user_input_str)
        except ValueError: VARS[result_var_name] = user_input_str
    except Exception as e: print(f"[ERROR] 입력 처리 오류: {line} -> {e}")

def evaluate_condition(condition_line):
    """조건 평가: '권일이가 [조건] 이면'"""
    try:
        condition = condition_line.replace('권일이가', '').replace('이면', '').strip()
        if '==' not in condition and '=' in condition: condition = condition.replace('=', '==')
        eval_condition = substitute_vars(condition)
        return bool(eval(eval_condition))
    except Exception as e:
        print(f"[ERROR] 조건 평가 오류: {condition_line} -> {e}")
        return False

# --- 메인 실행 흐름 함수 ---

def run_gwonir_file(file_path):
    """궈니르 파일을 실행하고 최종 변수 상태를 출력합니다."""
    global VARS, OUTPUT_BUFFER
    VARS = {}
    OUTPUT_BUFFER = "" 
    
    print(f"==========================================")
    print(f"| 궈니르 언어 인터프리터 (파이썬) 실행 |")
    print(f"| 파일: {file_path} ")
    print(f"==========================================")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            final_commands = []
            for line in lines:
                cleaned_line = line.strip()
                
                # 1. 인라인 주석 제거
                if '#' in cleaned_line:
                    cleaned_line = cleaned_line.split('#', 1)[0].strip()
                    
                # 2. 시작/끝/빈 줄 무시
                if not cleaned_line or cleaned_line.startswith('권일이는') or cleaned_line == '귀여워':
                    continue
                
                # 3. 한 줄에 하나의 명령어만 처리
                final_commands.append(cleaned_line)

            current_index = 0
            while current_index < len(final_commands):
                cleaned_line = final_commands[current_index]
                
                next_index = current_index + 1
                
                # --- 명령어 처리 ---
                
                # 1. 조건문 처리 (IF/ELSE)
                if cleaned_line.startswith('권일이가') and cleaned_line.endswith('이면'):
                    
                    if evaluate_condition(cleaned_line):
                        next_index = current_index + 1 # 참: 다음 명령어(IF 본문) 실행
                    else:
                        next_index = current_index + 2 # 거짓: 다음 명령어(IF 본문) 건너뛰고 ELSE 로직으로 이동
                
                # 2. 루프 종료
                elif cleaned_line == '권일이가 멈춰':
                    print("\n--- [Break] '권일이가 멈춰' 명령으로 실행을 중단합니다. ---")
                    break
                
                # 3. 실행 명령어
                elif cleaned_line.startswith('권일아 기억해!'):
                    execute_assignment(cleaned_line)
                
                elif cleaned_line.startswith('권일아 말해라('):
                    execute_print(cleaned_line)
                    
                elif cleaned_line.startswith('권일아 계산해!'):
                    execute_calculation(cleaned_line)
                
                elif cleaned_line.startswith('권일아 니가 원하는거 함 골라봐라'):
                    execute_input(cleaned_line)

                # 4. Unknown command
                else:
                    print(f"[WARN] 알 수 없는 명령어 처리: {cleaned_line}")

                # --- 5. IF 본문 실행 후, ELSE 블록 점프 ---
                # 현재 명령어(current_index)가 IF 본문이었고, 다음 명령이 ELSE 블록이라면 건너뜁니다.
                if current_index > 0 and \
                   final_commands[current_index-1].startswith('권일이가') and \
                   final_commands[current_index-1].endswith('이면') and \
                   evaluate_condition(final_commands[current_index-1]):
                   
                   # 그리고 다음 명령이 ELSE 시작(또다른 IF)이라면
                   if current_index + 1 < len(final_commands) and \
                      final_commands[current_index + 1].startswith('권일이가') and \
                      final_commands[current_index + 1].endswith('이면'):
                      
                      # IF 본문 1줄 실행 후, 다음 ELSE IF 명령어 건너뛰기
                      next_index = current_index + 2 

                # 인덱스 업데이트
                current_index = next_index
            
            if OUTPUT_BUFFER:
                 print(OUTPUT_BUFFER)

            print("\n--- 실행 완료 (최종 변수 상태) ---")
            print(VARS)
            print("---------------------------------")
            
    except FileNotFoundError: print(f"[ERROR] 파일을 찾을 수 없습니다: {file_path}")
    except Exception as e: print(f"[ERROR] 실행 중 치명적인 오류 발생: {e}")


# --- 메인 실행 블록 (gwonir 명령어 실행을 위해 필수!) ---
def main():
    """pip 설치 후 'gwonir [파일경로]' 명령어를 실행하기 위한 진입점."""
    # 실행 시 파일 경로(sys.argv[1])를 받습니다.
    if len(sys.argv) < 2:
        print("사용법: gwonir [궈니르 파일 경로]")
        return
    
    file_path = sys.argv[1]
    run_gwonir_file(file_path)

if __name__ == "__main__":
    main()