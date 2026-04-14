use my_cat;

-- 게시판 테이블
CREATE TABLE board (
    no INT AUTO_INCREMENT PRIMARY KEY,         -- 글 번호 (PK)
    title VARCHAR(255) NOT NULL,               -- 글 제목
    writer VARCHAR(50) NOT NULL,               -- 작성자
    text TEXT NOT NULL,                        -- 글 내용
    category VARCHAR(50) NOT NULL,             -- 글 카테고리
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 작성 시각
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 댓글 테이블
CREATE TABLE comment (
    commentId INT NOT NULL,                    -- 댓글 ID (PK 용도)
    boardNo INT NOT NULL,                       -- 해당 글 번호 (FK)
    writer VARCHAR(50) NOT NULL,                -- 댓글 작성자
    text TEXT NOT NULL,                         -- 댓글 내용
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 작성 시각
    PRIMARY KEY (commentId, boardNo),           -- 복합 PK
    FOREIGN KEY (boardNo) REFERENCES board(no) ON DELETE CASCADE
);

-- 회원가입 관련 테이블
CREATE TABLE member (
    Id VARCHAR(50) PRIMARY KEY,                 -- 회원 아이디 (PK)
    Pw VARCHAR(255) NOT NULL,                   -- 비밀번호 (암호화 저장 권장)
    email VARCHAR(255),                         -- 이메일
    Game INT DEFAULT 0,                          -- 게임 수
    Win INT DEFAULT 0,                           -- 승
    Lose INT DEFAULT 0,                          -- 패
    Draw INT DEFAULT 0                           -- 무승부
);

