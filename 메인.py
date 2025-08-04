import math
from copy import deepcopy

"""
주의사항: print() 함수 사용 시, 반드시 flush=True 설정할 것!
        예: print(*args, flush=True)
        그렇지 않으면 TLE(Time Limit Exceeded)가 발생할 수 있음.
"""

# 게임 트리 탐색 최대 깊이
DEPTH = 2

# 보드 크기 정의
BOARD_ROW = 10 # (0,0) ~ (9,0)
BOARD_COLUMN = 17 # (0,0) ~ (0,16)

# 패스할 때 사용하는 무효 좌표
PASS = [-1, -1, -1, -1]


class Game:
    def __init__(self, board, first):
        # 보드 상태 저장
        self.board = board
        # 점령 여부 저장용 보드 (1: 내 땅, -1: 상대 땅, 0: 미점령)
        self.territory_board = [
            [0 for _ in range(BOARD_COLUMN)] for _ in range(BOARD_ROW)
        ]
        self.turn = 0
        # self.first = first (필요시 활성화)

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

    def _calculate_board_value(self):
        # 현재 territory_board 기준으로 점수 계산
        return sum([sum(row) for row in self.territory_board])

    def _simulate_negamax(self, alpha: int, beta: int, depth: int, color: int) -> tuple[int, list[int]]:
        """
        Negamax + Alpha-Beta 기반 재귀 탐색
        Args:
            alpha: 현재까지의 최대 하한값
            beta: 현재까지의 최소 상한값
            depth: 현재 깊이
            color: 1 (내 턴) 또는 -1 (상대 턴)

        Returns:
            (현재 상태의 최대 점수, 최적 수)
        """
        original_board = deepcopy(self.board)
        original_territory_board = deepcopy(self.territory_board)
        best_move = PASS
        best_value = -math.inf
        is_terminal = True

        if depth == DEPTH:
            return color * self._calculate_board_value(), PASS

        for r1 in range(BOARD_ROW):
            for r2 in range(r1, BOARD_ROW):
                for c1 in range(BOARD_COLUMN):
                    for c2 in range(c1, BOARD_COLUMN):
                        if not self.isValid(r1, c1, r2, c2):
                            continue

                        is_terminal = False
                        self.updateMove(r1, c1, r2, c2, color == 1)

                        # 다음 턴: color 뒤집어서 상대 입장
                        value, _ = self._simulate_negamax(-beta, -alpha, depth + 1, -color)
                        value = -value  # 점수 반전

                        if value > best_value:
                            best_value = value
                            best_move = [r1, c1, r2, c2]
                            alpha = max(alpha, value)

                        self.restoreMove(r1, c1, r2, c2, original_board, original_territory_board)

                        if alpha >= beta:
                            return alpha, best_move

        if is_terminal:
            return color * self._calculate_board_value(), PASS
        else:
            return best_value, best_move

    def calculateMove(self, _myTime, _oppTime) -> list[int]:
        """
        현재 상태에서 최적 수 계산

        Returns:
            (r1, c1, r2, c2) 형태의 수
        """

        global DEPTH

        if self.turn <= 5:
            pass
        elif self.turn <= 9:
            DEPTH = 3
        elif self.turn <= 12:
            DEPTH = 4
        elif self.turn <= 14:
            DEPTH = 5
        else:
            DEPTH = min(DEPTH + 1, 100)  # 최대 100까지 증가

        _, best_move = self._simulate_negamax(-math.inf, math.inf, 0, 1)
        self.turn += 1
        return best_move

    def updateOpponentAction(self, action, _time) -> None:
        # 상대 수 반영
        self.updateMove(*action, False)

    def updateMove(self, r1, c1, r2, c2, is_my_turn) -> None:
        # 수를 보드에 적용
        if r1 == c1 == r2 == c2 == -1:
            return
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.board[r][c] = 0  # 해당 칸 숫자는 사용했으므로 0 처리
                self.territory_board[r][c] = 1 if is_my_turn else -1

    def restoreMove(self, r1, c1, r2, c2, original_board, original_territory_board) -> None:
        # 이전 상태로 복구
        if r1 == c1 == r2 == c2 == -1:
            return
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                self.board[r][c] = original_board[r][c]
                self.territory_board[r][c] = original_territory_board[r][c]


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
            # 게임 초기 보드 설정
            board = [list(map(int, row)) for row in param]
            global game
            game = Game(board, first)
            continue

        if command == "TIME":
            # 내 턴일 경우, 최적 수 계산 후 실행
            myTime, oppTime = map(int, param)
            ret = game.calculateMove(myTime, oppTime)
            game.updateMove(*ret, True)
            print(*ret, flush=True)
            continue

        if command == "OPP":
            # 상대의 수를 보드에 반영
            r1, c1, r2, c2, time = map(int, param)
            game.updateOpponentAction((r1, c1, r2, c2), time)
            continue

        if command == "FINISH":
            # 게임 종료
            break

        # 예외 처리
        assert False, f"Invalid command {command}"


if __name__ == "__main__":
    main()
