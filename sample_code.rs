use std::io::{self, BufRead, Write};
use std::process::exit;

// 게임 상태를 관리하는 구조체
struct Game {
    board: Vec<Vec<i32>>, // 게임 보드 (2차원 벡터)
    _first: bool,         // 선공 여부
    passed: bool,         // 마지막 턴에 패스했는지 여부
}

type Move = Option<(usize, usize, usize, usize)>;

impl Game {
    // Game 생성자
    fn new(board: Vec<Vec<i32>>, first: bool) -> Self {
        Game {
            board,
            _first: first,
            passed: false,
        }
    }

    // 사각형 (r1, c1) ~ (r2, c2)이 유효한지 검사 (합이 10이고, 네 변을 모두 포함)
    fn is_valid(&self, r1: usize, c1: usize, r2: usize, c2: usize) -> bool {
        let mut sums = 0;
        let mut r1fit = false;
        let mut c1fit = false;
        let mut r2fit = false;
        let mut c2fit = false;

        for r in r1..=r2 {
            for c in c1..=c2 {
                if self.board[r][c] != 0 {
                    sums += self.board[r][c];
                    if r == r1 {
                        r1fit = true;
                    }
                    if r == r2 {
                        r2fit = true;
                    }
                    if c == c1 {
                        c1fit = true;
                    }
                    if c == c2 {
                        c2fit = true;
                    }
                }
            }
        }
        sums == 10 && r1fit && r2fit && c1fit && c2fit
    }

    // ================================================================
    // ===================== [필수 구현] ===============================
    // 합이 10인 유효한 사각형을 찾아 Some((r1, c1, r2, c2))로 반환
    // 없으면 None 반환 (패스 의미)
    // ================================================================
    fn calculate_move(&self, _my_time: i32, _opp_time: i32) -> Move {
        // 가로로 인접한 두 칸을 선택했을 때 유효하면 선택하는 전략
        for r1 in 0..self.board.len() {
            for c1 in 0..self.board[r1].len() - 1 {
                let r2 = r1;
                let c2 = c1 + 1;
                if self.is_valid(r1, c1, r2, c2) {
                    return Some((r1, c1, r2, c2));
                }
            }
        }
        None // 유효한 사각형이 없으면 패스
    }
    // =================== [필수 구현 끝] =============================

    // 상대방의 수를 받아 보드에 반영
    fn update_opponent_action(&mut self, action: Move, _time: i32) {
        self.update_move(action, false);
    }

    // 주어진 수를 보드에 반영 (칸을 0으로 지움)
    fn update_move(&mut self, action: Move, _is_my_move: bool) {
        let Some((r1, c1, r2, c2)) = action else {
            self.passed = true;
            return;
        };

        for r in r1..=r2 {
            for c in c1..=c2 {
                self.board[r][c] = 0;
            }
        }
        self.passed = false;
    }
}

// 표준 입력을 통해 명령어를 처리하는 메인 함수
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
                // 선공 여부 확인
                let turn = parts.next().unwrap();
                _first = turn == "FIRST";
                println!("OK");
                io::stdout().flush().unwrap();
            }
            "INIT" => {
                // 보드 초기화
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
                // 내 턴: 수 계산 및 실행
                let my_time: i32 = parts.next().unwrap().parse().unwrap();
                let opp_time: i32 = parts.next().unwrap().parse().unwrap();
                let game = game.as_mut().unwrap();
                let ret = game.calculate_move(my_time, opp_time);
                game.update_move(ret, true);
                if let Some((r1, c1, r2, c2)) = ret {
                    println!("{} {} {} {}", r1, c1, r2, c2);
                } else {
                    println!("-1 -1 -1 -1");
                }
                io::stdout().flush().unwrap();
            }
            "OPP" => {
                // 상대 턴 반영
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
                game.as_mut()
                    .unwrap()
                    .update_opponent_action(opponent_move, time);
            }
            "FINISH" => break,
            _ => {
                // 잘못된 명령 처리
                eprintln!("Invalid command: {}", command);
                exit(1);
            }
        }
    }
}
