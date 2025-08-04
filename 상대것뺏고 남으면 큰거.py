def isValidStatic(self, board, r1, c1, r2, c2):
    sums = 0
    r1fit = c1fit = r2fit = c2fit = False

    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            if board[r][c] != 0:
                sums += board[r][c]
                if r == r1: r1fit = True
                if r == r2: r2fit = True
                if c == c1: c1fit = True
                if c == c2: c2fit = True

    return sums == 10 and r1fit and r2fit and c1fit and c2fit

def isSafeRectangle(self, r1, c1, r2, c2):
    temp_board = [row[:] for row in self.board]
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            temp_board[r][c] = 0

    rows = len(temp_board)
    cols = len(temp_board[0]) if temp_board else 0

    for sr1 in range(rows):
        for sr2 in range(sr1, rows):
            for sc1 in range(cols):
                for sc2 in range(sc1, cols):
                    if self.isValidStatic(temp_board, sr1, sc1, sr2, sc2):
                        return False
    return True

def isOnEdge(self, r1, c1, r2, c2):
    N = len(self.board)
    return r1 == 0 or r2 == N - 1 or c1 == 0 or c2 == N - 1

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

    # 내 점령 칸(-2)을 0으로 임시 치환
    temp_my_positions = []
    for r in range(N):
        for c in range(N):
            if self.board[r][c] == -2:
                self.board[r][c] = 0
                temp_my_positions.append((r, c))

    # 상대 칸 위치 확인
    self.updateOpponentPositions()

    if self.opponent_positions:
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
                                        stealCount -= 1
                            if stealCount > maxSteal:
                                maxSteal = stealCount
                                bestMove = (r1, c1, r2, c2)

    # 복원
    for r, c in temp_my_positions:
        self.board[r][c] = -2

    # 🔁 대안 전략: 반격할 곳이 없다면, 안전한 최대 사각형 점령
    if maxSteal <= 0:
        maxArea = 0
        for r1 in range(N):
            for r2 in range(r1, N):
                for c1 in range(N):
                    for c2 in range(c1, N):
                        if self.isValid(r1, c1, r2, c2) and self.isSafeRectangle(r1, c1, r2, c2):
                            area = (r2 - r1 + 1) * (c2 - c1 + 1)
                            if area > maxArea:
                                maxArea = area
                                bestMove = (r1, c1, r2, c2)

    return bestMove




