// Rust 버섯 게임 AI (Negamax + AlphaBeta) - 학습용 자세한 주석 포함

// ───────────────────────────────────────────────
// 필요한 표준 라이브러리 불러오기
use std::io::{self, BufRead, Write}; // 입력, 출력 관련 모듈
use std::process::exit;               // 프로그램 강제 종료에 사용
use std::cmp::max;                    // 두 수 중 큰 값을 반환하는 함수

// ───────────────────────────────────────────────
// 상수 정의
const ROWS: usize = 10;  // 보드의 세로 크기
const COLS: usize = 17;  // 보드의 가로 크기
const DEPTH: usize = 2;  // 미니맥스 탐색의 최대 깊이

// 전역 영역 점령 정보
// TERRITORY[r][c] = 0이면 미점령, 1이면 내 영역, -1이면 상대 영역
static mut TERRITORY: [[i32; COLS]; ROWS] = [[0; COLS]; ROWS];

// ───────────────────────────────────────────────
// 게임 상태를 저장하는 구조체
struct Game {
    board: Vec<Vec<i32>>, // 현재 버섯 보드 상태 (숫자 버섯들)
    _first: bool,          // 내가 선공인지 여부
    passed: bool,          // 직전 턴에 패스했는지 여부
    turn_counter: usize,   // 턴 수 (0부터 시작)
}

impl Game {
    // 생성자: 새로운 Game 객체를 초기화
    fn new(board: Vec<Vec<i32>>, first: bool) -> Self {
        Game {
            board,
            _first: first,
            passed: false,
            turn_counter: 0,
        }
    }

    // 주어진 사각형(r1,c1) ~ (r2,c2)이 유효한 선택인지 확인
    fn is_valid(&self, r1: usize, c1: usize, r2: usize, c2: usize) -> bool {
        let mut sums = 0;             // 버섯 숫자의 합
        let mut border_flags = 0u8;   // 각 방향에 버섯 존재 여부 비트 플래그

        for r in r1..=r2 {
            for c in c1..=c2 {
                let val = self.board[r][c];
                if val != 0 {
                    sums += val;
                    if sums > 10 {
                        return false; // 합이 10 초과면 유효하지 않음
                    }
                    // 각 방향에 버섯이 존재하는지 비트 설정
                    if r == r1 { border_flags |= 1 << 0; } // 위
                    if r == r2 { border_flags |= 1 << 1; } // 아래
                    if c == c1 { border_flags |= 1 << 2; } // 좌
                    if c == c2 { border_flags |= 1 << 3; } // 우
                }
            }
        }
        // 합이 10이고, 네 방향 모두 버섯이 있어야 유효
        sums == 10 && border_flags == 0b1111
    }

    // 현재 보드에서 내 점령 수 - 상대 점령 수 반환
    fn calculate_board_value(&self) -> i32 {
        let mut total = 0;
        unsafe {
            for r in 0..ROWS {
                for c in 0..COLS {
                    total += TERRITORY[r][c]; // 내 영역은 +1, 상대는 -1
                }
            }
        }
        total
    }

    // Negamax + 알파-베타 가지치기 알고리즘으로 최적 수 탐색
    fn simulate(&mut self, mut alpha: i32, beta: i32, depth: usize, color: i32)
        -> (i32, Option<(usize, usize, usize, usize)>) {

        // 탐색 종료 조건: 최대 깊이 또는 턴 제한 도달
        if depth == DEPTH || self.turn_counter == 10 {
            return (color * self.calculate_board_value(), None);
        }

        let mut best_value = i32::MIN;        // 현재 최대 점수
        let mut best_move = None;             // 그에 해당하는 수
        let board_backup = self.board.clone(); // 보드 상태 백업

        // 테리토리 상태 백업 (전역 변수)
        let mut territory_backup = [[0; COLS]; ROWS];
        unsafe {
            for r in 0..ROWS {
                for c in 0..COLS {
                    territory_backup[r][c] = TERRITORY[r][c];
                }
            }
        }

        let mut found = false; // 유효한 수를 찾았는지 여부

        // 모든 가능한 사각형을 시도
        for r1 in 0..ROWS {
            for r2 in r1..ROWS {
                for c1 in 0..COLS {
                    for c2 in c1..COLS {
                        if !self.is_valid(r1, c1, r2, c2) {
                            continue;
                        }
                        found = true; // 유효한 수 발견

                        self.make_move(r1, c1, r2, c2, color); // 수 적용
                        self.turn_counter += 1;

                        // 상대의 최선 수를 재귀적으로 계산
                        let (val, _) = self.simulate(-beta, -alpha, depth + 1, -color);

                        self.turn_counter -= 1;
                        let val = -val; // negamax: 점수 반전
                        self.restore(board_backup.clone(), &territory_backup); // 복원

                        if val > best_value {
                            best_value = val;
                            best_move = Some((r1, c1, r2, c2));
                            alpha = max(alpha, val);
                        }
                        // 가지치기: 현재 수가 상대가 허용할 수 없는 수준이면 더 볼 필요 없음
                        if alpha >= beta {
                            return (alpha, best_move);
                        }
                    }
                }
            }
        }

        // 둘 수 있는 수가 없으면 패스 (현재 점수 반환)
        if !found {
            return (color * self.calculate_board_value(), None);
        }

        (best_value, best_move)
    }

    // 수를 보드와 테리토리에 적용
    fn make_move(&mut self, r1: usize, c1: usize, r2: usize, c2: usize, color: i32) {
        unsafe {
            for r in r1..=r2 {
                for c in c1..=c2 {
                    self.board[r][c] = 0;       // 해당 버섯 제거
                    TERRITORY[r][c] = color;    // 점령 상태 설정
                }
            }
        }
    }

    // 보드 및 테리토리 상태 복원
    fn restore(&mut self, board: Vec<Vec<i32>>, territory: &[[i32; COLS]; ROWS]) {
        self.board = board;
        unsafe {
            for r in 0..ROWS {
                for c in 0..COLS {
                    TERRITORY[r][c] = territory[r][c];
                }
            }
        }
    }

    // 현재 차례에 둘 최적 수 계산
    fn calculate_move(&mut self, _my_time: i32, _opp_time: i32)
        -> Option<(usize, usize, usize, usize)> {
        let (_val, mv) = self.simulate(i32::MIN, i32::MAX, 0, 1);
        mv
    }

    // 상대의 수를 처리하여 보드에 반영
    fn update_opponent_action(&mut self, action: Option<(usize, usize, usize, usize)>, _time: i32) {
        self.update_move(action, false);
    }

    // 수를 보드에 실제 반영
    fn update_move(&mut self, action: Option<(usize, usize, usize, usize)>, is_my_move: bool) {
        let Some((r1, c1, r2, c2)) = action else {
            self.passed = true; // PASS일 경우
            return;
        };
        let color = if is_my_move { 1 } else { -1 }; // 내 수면 1, 상대면 -1
        self.make_move(r1, c1, r2, c2, color);
        self.passed = false;
        self.turn_counter += 1;
    }
}

// ───────────────────────────────────────────────
// 메인 함수: 심판의 명령을 받아 처리하는 게임 루프
fn main() {
    let stdin = io::stdin();
    let mut game: Option<Game> = None;
    let mut _first = false;

    for line in stdin.lock().lines() {
        let line = line.unwrap();
        let mut parts = line.split_whitespace();

        let command = match parts.next() {
            Some(cmd) => cmd,
            None => continue,
        };

        match command {
            "READY" => {
                let turn = parts.next().unwrap();
                _first = turn == "FIRST";
                println!("OK");
                io::stdout().flush().unwrap();
            }
            "INIT" => {
                let mut board = Vec::new();
                for row in parts {
                    let board_row: Vec<i32> = row
                        .chars()
                        .map(|c| c.to_digit(10).unwrap() as i32)
                        .collect();
                    board.push(board_row);
                }
                game = Some(Game::new(board, _first));
            }
            "TIME" => {
                let my_time: i32 = parts.next().unwrap().parse().unwrap();
                let opp_time: i32 = parts.next().unwrap().parse().unwrap();
                let game = game.as_mut().unwrap();
                let ret = game.calculate_move(my_time, opp_time);
                game.update_move(ret, true);
                if let Some((r1, c1, r2, c2)) = ret {
                    println!("{} {} {} {}", r1, c1, r2, c2);
                } else {
                    println!("-1 -1 -1 -1"); // PASS
                }
                io::stdout().flush().unwrap();
            }
            "OPP" => {
                let r1: i32 = parts.next().unwrap().parse().unwrap();
                let c1: i32 = parts.next().unwrap().parse().unwrap();
                let r2: i32 = parts.next().unwrap().parse().unwrap();
                let c2: i32 = parts.next().unwrap().parse().unwrap();
                let time: i32 = parts.next().unwrap().parse().unwrap();
                let opponent_move = if r1 == -1 && c1 == -1 && r2 == -1 && c2 == -1 {
                    None
                } else {
                    Some((r1 as usize, c1 as usize, r2 as usize, c2 as usize))
                };
                game.as_mut().unwrap().update_opponent_action(opponent_move, time);
            }
            "FINISH" => break, // 게임 종료
            _ => {
                eprintln!("Invalid command: {}", command);
                exit(1);
            }
        }
    }
}
