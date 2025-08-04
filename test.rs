use std::io::{self, BufRead, Write};
use std::process::exit;
use std::cmp::max;

const ROWS: usize = 10;
const COLS: usize = 17;
const DEPTH: usize = 2;

const PASS: (usize, usize, usize, usize) = (usize::MAX, usize::MAX, usize::MAX, usize::MAX);

type Move = Option<(usize, usize, usize, usize)>;

static mut TERRITORY: [[i32; COLS]; ROWS] = [[0; COLS]; ROWS];
static mut TURN: usize = 0;

struct Game {
    board: Vec<Vec<i32>>,
    _first: bool,
    passed: bool,
}

impl Game {
    fn new(board: Vec<Vec<i32>>, first: bool) -> Self {
        Game {
            board,
            _first: first,
            passed: false,
        }
    }

    fn is_valid(&self, r1: usize, c1: usize, r2: usize, c2: usize) -> bool {
        let mut sums = 0;
        let mut border_flags = 0u8;

        for r in r1..=r2 {
            for c in c1..=c2 {
                let val = self.board[r][c];
                if val != 0 {
                    sums += val;
                    if sums > 10 {
                        return false;
                    }
                    if r == r1 { border_flags |= 1 << 0; }
                    if r == r2 { border_flags |= 1 << 1; }
                    if c == c1 { border_flags |= 1 << 2; }
                    if c == c2 { border_flags |= 1 << 3; }
                }
            }
        }

        sums == 10 && border_flags == 0b1111
    }

    fn calculate_board_value(&self) -> i32 {
        unsafe { TERRITORY.iter().flatten().sum() }
    }

    fn simulate(&mut self, mut alpha: i32, beta: i32, depth: usize, color: i32) -> (i32, Move) {
        unsafe {
            if depth == DEPTH || TURN >= 10 {
                return (color * self.calculate_board_value(), None);
            }
        }

        let mut best_value = i32::MIN;
        let mut best_move = None;
        let board_backup = self.board.clone();
        let mut territory_backup = [[0; COLS]; ROWS];

        unsafe {
            territory_backup = TERRITORY;
        }

        let mut found = false;

        for r1 in 0..ROWS {
            for r2 in r1..ROWS {
                for c1 in 0..COLS {
                    for c2 in c1..COLS {
                        if !self.is_valid(r1, c1, r2, c2) {
                            continue;
                        }
                        found = true;

                        self.make_move(r1, c1, r2, c2, color);
                        let (val, _) = self.simulate(-beta, -alpha, depth + 1, -color);
                        let val = -val;
                        self.restore(board_backup.clone(), territory_backup);

                        if val > best_value {
                            best_value = val;
                            best_move = Some((r1, c1, r2, c2));
                            alpha = max(alpha, val);
                        }
                        if alpha >= beta {
                            return (alpha, best_move);
                        }
                    }
                }
            }
        }

        if !found {
            return (color * self.calculate_board_value(), None);
        }
        (best_value, best_move)
    }

    fn make_move(&mut self, r1: usize, c1: usize, r2: usize, c2: usize, color: i32) {
        unsafe {
            for r in r1..=r2 {
                for c in c1..=c2 {
                    self.board[r][c] = 0;
                    TERRITORY[r][c] = color;
                }
            }
        }
    }

    fn restore(&mut self, board: Vec<Vec<i32>>, territory: [[i32; COLS]; ROWS]) {
        self.board = board;
        unsafe {
            TERRITORY = territory;
        }
    }

    fn calculate_move(&mut self, _my_time: i32, _opp_time: i32) -> Move {
        let (_val, mv) = self.simulate(i32::MIN, i32::MAX, 0, 1);
        unsafe {
            TURN += 1;
        }
        mv
    }

    fn update_opponent_action(&mut self, action: Move, _time: i32) {
        self.update_move(action, false);
    }

    fn update_move(&mut self, action: Move, is_my_move: bool) {
        let Some((r1, c1, r2, c2)) = action else {
            self.passed = true;
            return;
        };
        let color = if is_my_move { 1 } else { -1 };
        self.make_move(r1, c1, r2, c2, color);
        self.passed = false;
    }
}

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
                    println!("-1 -1 -1 -1");
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
                game.as_mut()
                    .unwrap()
                    .update_opponent_action(opponent_move, time);
            }
            "FINISH" => break,
            _ => {
                eprintln!("Invalid command: {}", command);
                exit(1);
            }
        }
    }
}
