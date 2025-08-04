# ================================
# Game 클래스: 게임 상태 관리
# ================================
class Game:

    def __init__(self, board, first):
        self.board = board            # 게임 보드 (2차원 배열)
        self.first = first            # 선공 여부
        self.passed = False           # 마지막 턴에 패스했는지 여부
        self.opponent_history = []
        self.turn = 1

    def get_opponent_positions(self):
        """필요할 때마다 opponent_history에서 계산"""
        positions = set()
        for r1, c1, r2, c2 in self.opponent_history:
            for r in range(r1, r2 + 1):
                for c in range(c1, c2 + 1):
                    positions.add((r, c))
        return positions

    # 사각형 (r1, c1) ~ (r2, c2)이 유효한지 검사 (합이 10이고, 네 변을 모두 포함)
    def isValid(self, r1, c1, r2, c2):
        """메모리 최적화된 유효성 검사"""
        sums = 0
        border_flags = 0  # 비트마스크로 4개 플래그를 1개 변수로
        # bit 0: top, bit 1: bottom, bit 2: left, bit 3: right
        
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if self.board[r][c] != 0:
                    sums += self.board[r][c]
                    # 조기 종료: 합이 10 초과
                    if sums > 10:
                        return False
                    
                    # 비트마스크로 테두리 플래그 업데이트
                    if r == r1: border_flags |= 1  # bit 0
                    if r == r2: border_flags |= 2  # bit 1  
                    if c == c1: border_flags |= 4  # bit 2
                    if c == c2: border_flags |= 8  # bit 3
        
        # 합이 10이고 모든 테두리가 커버되는지 확인 (15 = 1111 in binary)
        return sums == 10 and border_flags == 15

    # ================================================================
    # ===================== [필수 구현] ===============================
    # 합이 10인 유효한 사각형을 찾아 (r1, c1, r2, c2) 튜플로 반환
    # 없으면 (-1, -1, -1, -1) 반환 (패스 의미)
    # ================================================================
    def _get_quadrant_range(self, rows, cols):
        """턴에 따른 4등분 탐색 범위 계산"""
        if self.turn == 1:
            return 0, rows, 0, cols
        
        quadrant = self.turn % 4
        if quadrant == 0:  # 좌상단
            r_start, r_end = 0, (rows + 1) // 2
            c_start, c_end = 0, (cols + 1) // 2
        elif quadrant == 1:  # 우상단
            r_start, r_end = 0, (rows + 1) // 2
            c_start, c_end = (cols + 1) // 2, cols
        elif quadrant == 2:  # 좌하단
            r_start, r_end = (rows + 1) // 2, rows
            c_start, c_end = 0, (cols + 1) // 2
        else:  # 우하단
            r_start, r_end = (rows + 1) // 2, rows
            c_start, c_end = (cols + 1) // 2, cols

        # ±2칸 보정
        r_start = max(0, r_start - 2)
        r_end = min(rows, r_end + 2)
        c_start = max(0, c_start - 2)
        c_end = min(cols, c_end + 2)
        
        return r_start, r_end, c_start, c_end

    # def is_vulnerable_after_occupy(self, r1, c1, r2, c2):
    #     """이 사각형을 점령한 후, 해당 영역이 다시 탈환당할 수 있는지 검사"""
    #     N = len(self.board)
    #     own_positions = set((r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))

    #     for r, c in own_positions:
    #         # (r, c) 주변 ±2칸 탐색
    #         for vr in range(max(0, r - 2), min(N, r + 3)):
    #             for vc in range(max(0, c - 2), min(N, c + 3)):
    #                 for hr in range(vr, min(N, vr + 6)):
    #                     for hc in range(vc, min(N, vc + 6)):
    #                         if self.isValid(vr, vc, hr, hc):
    #                             # 유효한 사각형이 내 영역을 포함하면 탈환 위험
    #                             if any((tr, tc) in own_positions for tr in range(vr, hr + 1) for tc in range(vc, hc + 1)):
    #                                 return True  # 위험
    #     return False  # 안전

    def _find_max_area_rectangle(self, r_start, r_end, c_start, c_end):
        """주어진 범위에서 최대 면적 사각형 찾기 - 큰 것부터 탐색"""
        bestMove = (-1, -1, -1, -1)
        max_height = r_end - r_start
        max_width = c_end - c_start
        
        # 큰 면적부터 탐색 (조기 종료)
        for height in range(max_height, 0, -1):
            for width in range(max_width, 0, -1):
                # 해당 높이와 너비로 가능한 모든 위치 검사
                for r1 in range(r_start, r_end - height + 1):
                    r2 = r1 + height - 1
                    for c1 in range(c_start, c_end - width + 1):
                        c2 = c1 + width - 1
                        
                        if self.isValid(r1, c1, r2, c2):
                            bestMove = (r1, c1, r2, c2)
                            # 첫 번째로 찾은 것이 최대 면적이므로 즉시 반환
                            return bestMove
        
        # 아무것도 찾지 못한 경우
        return bestMove


    def _find_max_steal_rectangle(self, opp_r1, opp_c1, opp_r2, opp_c2):
        """상대 사각형 주변에서 최대 steal 사각형 찾기"""
        N = len(self.board)
        opponent_positions = self.get_opponent_positions()

        max_steal = -1
        best_rect = (-1, -1, -1, -1)

        for r1 in range(max(0, opp_r1 - 3), min(N, opp_r2 + 4)):
            for r2 in range(r1, min(N, r1 + 8)):
                for c1 in range(max(0, opp_c1 - 3), min(N, opp_c2 + 4)):
                    for c2 in range(c1, min(N, c1 + 8)):
                        if self.isValid(r1, c1, r2, c2):
                            steal_count = sum(
                                (r, c) in opponent_positions
                                for r in range(r1, r2 + 1)
                                for c in range(c1, c2 + 1)
                            )
                            area = (r2 - r1 + 1) * (c2 - c1 + 1)

                            # 가장 많이 탈환하면서, 넓은 사각형 우선
                            if steal_count > max_steal or (steal_count == max_steal and area > (best_rect[2] - best_rect[0] + 1) * (best_rect[3] - best_rect[1] + 1)):
                                max_steal = steal_count
                                best_rect = (r1, c1, r2, c2)

        return best_rect

    def calculateMove(self, _myTime=0, _oppTime=0):
        """메인 로직"""
        rows = len(self.board)
        cols = len(self.board[0])
        
        # 선공인 경우
        if self.first:
            if self.turn <= 4:
                # 초반: 큰 면적 찾기
                r_start, r_end, c_start, c_end = self._get_quadrant_range(rows, cols)
                bestMove = self._find_max_area_rectangle(r_start, r_end, c_start, c_end)
            else:
                if self.opponent_history[-1] == (-1, -1, -1, -1):
                    # 상대 패스: 면적 우선
                    r_start, r_end, c_start, c_end = self._get_quadrant_range(rows, cols)
                    bestMove = self._find_max_area_rectangle(r_start, r_end, c_start, c_end)
                else:
                    # 상대가 수를 둠: steal 전략
                    opp_r1, opp_c1, opp_r2, opp_c2 = self.opponent_history[-1]
                    bestMove = self._find_max_steal_rectangle(opp_r1, opp_c1, opp_r2, opp_c2)
                    if bestMove == (-1, -1, -1, -1):
                        r_start, r_end, c_start, c_end = self._get_quadrant_range(rows, cols)
                        bestMove = self._find_max_area_rectangle(r_start, r_end, c_start, c_end)
        
        # 후공인 경우
        else:
            if self.turn <= 4:
                r_start, r_end, c_start, c_end = self._get_quadrant_range(rows, cols)
                bestMove = self._find_max_area_rectangle(r_start, r_end, c_start, c_end)
            else:
                if self.opponent_history[-1] == (-1, -1, -1, -1):
                    # 상대 패스: 면적 우선
                    r_start, r_end, c_start, c_end = self._get_quadrant_range(rows, cols)
                    bestMove = self._find_max_area_rectangle(r_start, r_end, c_start, c_end)
                else:
                    # 상대가 수를 둠: steal 전략 (후공은 8칸 제한)
                    opp_r1, opp_c1, opp_r2, opp_c2 = self.opponent_history[-1]
                    bestMove = self._find_max_steal_rectangle(opp_r1, opp_c1, opp_r2, opp_c2)
                    if bestMove == (-1, -1, -1, -1):
                        r_start, r_end, c_start, c_end = self._get_quadrant_range(rows, cols)
                        bestMove = self._find_max_area_rectangle(r_start, r_end, c_start, c_end)
        
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
