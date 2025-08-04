def findBestCounterAttackRectangle(self, opp_r1, opp_c1, opp_r2, opp_c2):
    N = len(self.board)
    maxSteal = -1
    bestMove = (-1, -1, -1, -1)

    # 주변 ±2 범위 내에서 탐색
    for r1 in range(max(0, opp_r1 - 2), min(N, opp_r2 + 3)):
        for r2 in range(r1, min(N, opp_r2 + 3)):
            for c1 in range(max(0, opp_c1 - 2), min(N, opp_c2 + 3)):
                for c2 in range(c1, min(N, opp_c2 + 3)):
                    if self.isValid(r1, c1, r2, c2):
                        stealCount = 0
                        for r in range(r1, r2 + 1):
                            for c in range(c1, c2 + 1):
                                if (r, c) in self.opponent_positions:
                                    stealCount += 1
                        if stealCount > maxSteal:
                            maxSteal = stealCount
                            bestMove = (r1, c1, r2, c2)
    return bestMove

def calculateMove(self, _myTime, _oppTime):
    N = len(self.board)
    maxSteal = -1
    bestMove = (-1, -1, -1, -1)

    # self.opponent_positions 없으면 계산 불가
    if not hasattr(self, 'opponent_positions') or not self.opponent_positions:
        return (-1, -1, -1, -1)

    # 내 점령 칸(-2)을 0으로 임시 치환
    temp_my_positions = []
    for r in range(N):
        for c in range(N):
            if self.board[r][c] == -2:
                self.board[r][c] = 0
                temp_my_positions.append((r, c))

    # 바운딩 박스 계산
    opp_rows = [r for (r, c) in self.opponent_positions]
    opp_cols = [c for (r, c) in self.opponent_positions]
    min_r, max_r = max(0, min(opp_rows) - 2), min(N - 1, max(opp_rows) + 2)
    min_c, max_c = max(0, min(opp_cols) - 2), min(N - 1, max(opp_cols) + 2)

    for r1 in range(min_r, max_r + 1):
        for r2 in range(r1, max_r + 1):
            for c1 in range(min_c, max_c + 1):
                for c2 in range(c1, max_c + 1):
                    if self.isValid(r1, c1, r2, c2):
                        stealCount = 0
                        for r in range(r1, r2 + 1):
                            for c in range(c1, c2 + 1):
                                if self.board[r][c] == 0:
                                    stealCount += 1
                                elif self.board[r][c] == -2:
                                    stealCount -= 1  # 🧠 이미 내가 점령한 칸은 제외

                        if stealCount > maxSteal:
                            maxSteal = stealCount
                            bestMove = (r1, c1, r2, c2)

    # 복원
    for r, c in temp_my_positions:
        self.board[r][c] = -2

    return bestMove if maxSteal > 0 else (-1, -1, -1, -1)



