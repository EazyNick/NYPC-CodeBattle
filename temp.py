# ================================
# Game 클래스: 게임 상태 관리
# ================================
class Game:

    def __init__(self, board, first):
        self.board = board            # 게임 보드 (2차원 배열)
        self.first = first            # 선공 여부
        self.passed = False           # 마지막 턴에 패스했는지 여부
        self.turn = 1

    # 사각형 (r1, c1) ~ (r2, c2)이 유효한지 검사 (합이 10이고, 네 변을 모두 포함)
    def isValid(self, r1, c1, r2, c2):
        sums = 0
        r1fit = c1fit = r2fit = c2fit = False

        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if self.board[r][c] != 0:
                    sums += self.board[r][c]
                    if sums > 10:
                        return False
                    if r == r1:
                        r1fit = True
                    if r == r2:
                        r2fit = True
                    if c == c1:
                        c1fit = True
                    if c == c2:
                        c2fit = True
        return sums == 10 and r1fit and r2fit and c1fit and c2fit

    # ================================================================
    # ===================== [필수 구현] ===============================
    # 합이 10인 유효한 사각형을 찾아 (r1, c1, r2, c2) 튜플로 반환
    # 없으면 (-1, -1, -1, -1) 반환 (패스 의미)
    # ================================================================
    def find_best_rectangle_early_termination(self, r_start, r_end, c_start, c_end):
        """조기 종료 조건을 활용한 탐색"""
        bestMove = (-1, -1, -1, -1)
        maxArea = 0
        
        # 바깥쪽 루프부터 큰 사각형 우선
        for height in range(r_end - r_start, 0, -1):  # 큰 높이부터
            for width in range(c_end - c_start, 0, -1):  # 큰 너비부터
                current_max_area = height * width
                
                # 조기 종료: 현재 가능한 최대 면적이 이미 찾은 것보다 작으면 스킵
                if current_max_area <= maxArea:
                    break
                
                for r1 in range(r_start, r_end - height + 1):
                    r2 = r1 + height - 1
                    for c1 in range(c_start, c_end - width + 1):
                        c2 = c1 + width - 1
                        
                        if self.isValid(r1, c1, r2, c2):
                            area = (r2 - r1 + 1) * (c2 - c1 + 1)
                            if area > maxArea:
                                maxArea = area
                                bestMove = (r1, c1, r2, c2)
        
        return bestMove

    def find_best_rectangle_bruteforce(self, r_start, r_end, c_start, c_end):
        """기존 완전 탐색 방식 (작은 범위용)"""
        bestMove = (-1, -1, -1, -1)
        maxArea = 0
        
        for r1 in range(r_start, r_end):
            for r2 in range(r1, r_end):
                for c1 in range(c_start, c_end):
                    for c2 in range(c1, c_end):
                        if self.isValid(r1, c1, r2, c2):
                            area = (r2 - r1 + 1) * (c2 - c1 + 1)
                            if area > maxArea:
                                maxArea = area
                                bestMove = (r1, c1, r2, c2)
        
        return bestMove

    def find_best_rectangle_hybrid(self, r_start, r_end, c_start, c_end):
        """하이브리드 접근: 작은 범위는 완전탐색, 큰 범위는 최적화"""
        total_cells = (r_end - r_start) * (c_end - c_start)
        
        # 범위가 작으면 기존 방식 (완전 탐색)
        if total_cells <= 64:  # 8x8 이하
            return self.find_best_rectangle_bruteforce(r_start, r_end, c_start, c_end)
        # 범위가 크면 최적화된 방식
        else:
            return self.find_best_rectangle_early_termination(r_start, r_end, c_start, c_end)


    def find_best_steal_move_optimized(self, opp_r1, opp_c1, opp_r2, opp_c2):
        """메모리 최적화된 steal 전략 탐색"""
        N = len(self.board)
        maxSteal = -1
        bestMove = (-1, -1, -1, -1)
        
        # 상대 사각형 주변 범위 설정
        search_range = 3
        r_start = max(0, opp_r1 - search_range)
        r_end = min(N, opp_r2 + search_range + 1)
        c_start = max(0, opp_c1 - search_range)
        c_end = min(N, opp_c2 + search_range + 1)
        
        # 최대 6칸 제한으로 탐색
        for r1 in range(r_start, r_end):
            for r2 in range(r1, min(N, r1 + 6)):
                for c1 in range(c_start, c_end):
                    for c2 in range(c1, min(N, c1 + 6)):
                        if self.isValid(r1, c1, r2, c2):
                            # steal 개수를 직접 계산 (set 생성하지 않음)
                            stealCount = 0
                            for r in range(r1, r2 + 1):
                                for c in range(c1, c2 + 1):
                                    if opp_r1 <= r <= opp_r2 and opp_c1 <= c <= opp_c2:
                                        stealCount += 1
                            
                            if stealCount > maxSteal:
                                maxSteal = stealCount
                                bestMove = (r1, c1, r2, c2)
        
        return bestMove


    def calculateMove(self, _myTime, _oppTime):
        """원본 로직을 유지하면서 최적화된 탐색 적용"""
        bestMove = (-1, -1, -1, -1)
        
        # 선공인 경우
        if self.first:
            # 4턴까지만 큰거 찾음
            if self.turn <= 4:
                rows = len(self.board)
                cols = len(self.board[0]) if self.board else 0

                # 영역 제한: 4등분
                if self.turn == 1:
                    r_start, r_end = 0, rows
                    c_start, c_end = 0, cols
                else:
                    quadrant = self.turn % 4
                    if quadrant == 0:  # 좌상단
                        r_start, r_end = 0, rows // 2
                        c_start, c_end = 0, cols // 2
                    elif quadrant == 1:  # 우상단
                        r_start, r_end = 0, rows // 2
                        c_start, c_end = cols // 2, cols
                    elif quadrant == 2:  # 좌하단
                        r_start, r_end = rows // 2, rows
                        c_start, c_end = 0, cols // 2
                    else:  # 우하단
                        r_start, r_end = rows // 2, rows
                        c_start, c_end = cols // 2, cols

                    # 탐색 범위 확장: ±2칸 보정
                    r_start = max(0, r_start - 2)
                    r_end = min(rows, r_end + 2)
                    c_start = max(0, c_start - 2)
                    c_end = min(cols, c_end + 2)

                # 최적화된 면적 탐색
                bestMove = self.find_best_rectangle_hybrid(r_start, r_end, c_start, c_end)
            
            else:  # 5턴 이후
                # 상대가 pass이면
                if not self.opponent_history:
                    rows = len(self.board)
                    cols = len(self.board[0]) if self.board else 0
                    # 면적 탐색 (위와 동일한 로직)
                    if self.turn == 1:
                        r_start, r_end = 0, rows
                        c_start, c_end = 0, cols
                    else:
                        quadrant = self.turn % 4
                        if quadrant == 0:
                            r_start, r_end = 0, rows // 2
                            c_start, c_end = 0, cols // 2
                        elif quadrant == 1:
                            r_start, r_end = 0, rows // 2
                            c_start, c_end = cols // 2, cols
                        elif quadrant == 2:
                            r_start, r_end = rows // 2, rows
                            c_start, c_end = 0, cols // 2
                        else:
                            r_start, r_end = rows // 2, rows
                            c_start, c_end = cols // 2, cols

                        r_start = max(0, r_start - 2)
                        r_end = min(rows, r_end + 2)
                        c_start = max(0, c_start - 2)
                        c_end = min(cols, c_end + 2)

                    bestMove = self.find_best_rectangle_hybrid(r_start, r_end, c_start, c_end)
                else:
                    # 상대가 수를 두었으면 steal 전략
                    opp_r1, opp_c1, opp_r2, opp_c2 = self.opponent_history[-1]
                    bestMove = self.find_best_steal_move_optimized(opp_r1, opp_c1, opp_r2, opp_c2)

        # 후공인 경우
        else:
            # 상대가 pass이면
            if not self.opponent_history:
                rows = len(self.board)
                cols = len(self.board[0]) if self.board else 0
                # 면적 탐색
                if self.turn == 1:
                    r_start, r_end = 0, rows
                    c_start, c_end = 0, cols
                else:
                    quadrant = self.turn % 4
                    if quadrant == 0:
                        r_start, r_end = 0, rows // 2
                        c_start, c_end = 0, cols // 2
                    elif quadrant == 1:
                        r_start, r_end = 0, rows // 2
                        c_start, c_end = cols // 2, cols
                    elif quadrant == 2:
                        r_start, r_end = rows // 2, rows
                        c_start, c_end = 0, cols // 2
                    else:
                        r_start, r_end = rows // 2, rows
                        c_start, c_end = cols // 2, cols

                    r_start = max(0, r_start - 2)
                    r_end = min(rows, r_end + 2)
                    c_start = max(0, c_start - 2)
                    c_end = min(cols, c_end + 2)

                bestMove = self.find_best_rectangle_memory_optimized(r_start, r_end, c_start, c_end)
            else:
                # 상대가 수를 두었으면 steal 전략
                opp_r1, opp_c1, opp_r2, opp_c2 = self.opponent_history[-1]
                bestMove = self.find_best_steal_move_optimized(opp_r1, opp_c1, opp_r2, opp_c2)

        self.turn += 1
        return bestMove
    # =================== [필수 구현 끝] =============================

    # 상대방의 수를 받아 보드에 반영
    def updateOpponentAction(self, action, _time):
        self.opponent_history = [action]  # 리스트 초기화

        self.updateMove(*action, False)

    # 주어진 수를 보드에 반영 (칸을 0으로 지움)
    def updateMove(self, r1, c1, r2, c2, _isMyMove):
        if r1 == c1 == r2 == c2 == -1:
            self.passed = True
            return
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.board[r][c] = 0
        self.passed = False


# ================================
# main(): 입출력 처리 및 게임 진행
# ================================
def main():
    while True:
        line = input().split()

        if len(line) == 0:
            continue

        command, *param = line

        if command == "READY":
            # 선공 여부 확인
            turn = param[0]
            global first
            first = turn == "FIRST"
            print("OK", flush=True)
            continue

        if command == "INIT":
            # 보드 초기화
            board = [list(map(int, row)) for row in param]
            global game
            game = Game(board, first)
            continue

        if command == "TIME":
            # 내 턴: 수 계산 및 실행
            myTime, oppTime = map(int, param)
            ret = game.calculateMove()
            game.updateMove(*ret, True)
            print(*ret, flush=True)
            continue

        if command == "OPP":
            # 상대 턴 반영
            r1, c1, r2, c2, time = map(int, param)
            game.updateOpponentAction((r1, c1, r2, c2), time)
            continue

        if command == "FINISH":
            break

        assert False, f"Invalid command {command}"


if __name__ == "__main__":
    main()
