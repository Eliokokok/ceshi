const BLOCK_SIZE = 30;
const GRID_WIDTH = 10;
const GRID_HEIGHT = 20;

const canvas = document.getElementById('gameCanvas');
const nextCanvas = document.getElementById('nextCanvas');
const ctx = canvas.getContext('2d');
const nextCtx = nextCanvas.getContext('2d');

canvas.width = BLOCK_SIZE * GRID_WIDTH;
canvas.height = BLOCK_SIZE * GRID_HEIGHT;
nextCanvas.width = BLOCK_SIZE * 4;
nextCanvas.height = BLOCK_SIZE * 4;

const SHAPES = {
    'I': [[0, 0], [-1, 0], [1, 0], [2, 0]],
    'O': [[0, 0], [1, 0], [0, 1], [1, 1]],
    'T': [[0, 0], [-1, 0], [1, 0], [0, 1]],
    'L': [[0, 0], [-1, 0], [1, 0], [1, 1]],
    'J': [[0, 0], [-1, 0], [1, 0], [-1, 1]],
    'S': [[0, 0], [-1, 0], [0, 1], [1, 1]],
    'Z': [[0, 0], [1, 0], [0, 1], [-1, 1]]
};

const COLORS = {
    'I': '#00f0f0',
    'O': '#f0f000',
    'T': '#a000f0',
    'L': '#f0a000',
    'J': '#0000f0',
    'S': '#00f000',
    'Z': '#f00000'
};

let grid = Array(GRID_HEIGHT).fill().map(() => Array(GRID_WIDTH).fill(null));
let currentPiece = null;
let nextPiece = null;
let score = 0;
let level = 1;
let lines = 0;
let gameLoop = null;
let isPaused = false;

class Piece {
    constructor(shape) {
        this.shape = shape;
        this.coords = SHAPES[shape];
        this.color = COLORS[shape];
        this.x = Math.floor(GRID_WIDTH / 2) - 1;
        this.y = 0;
        this.rotation = 0;
    }

    rotate() {
        const oldCoords = this.coords;
        this.coords = this.coords.map(([x, y]) => [-y, x]);
        if (this.checkCollision()) {
            this.coords = oldCoords;
        }
    }

    checkCollision() {
        return this.coords.some(([x, y]) => {
            const newX = this.x + x;
            const newY = this.y + y;
            return newX < 0 || newX >= GRID_WIDTH || 
                   newY >= GRID_HEIGHT ||
                   (newY >= 0 && grid[newY][newX] !== null);
        });
    }

    moveDown() {
        this.y++;
        if (this.checkCollision()) {
            this.y--;
            this.freeze();
            return false;
        }
        return true;
    }

    moveLeft() {
        this.x--;
        if (this.checkCollision()) {
            this.x++;
        }
    }

    moveRight() {
        this.x++;
        if (this.checkCollision()) {
            this.x--;
        }
    }

    freeze() {
        this.coords.forEach(([x, y]) => {
            const gridY = this.y + y;
            const gridX = this.x + x;
            if (gridY >= 0) {
                grid[gridY][gridX] = this.color;
            }
        });
        checkLines();
        currentPiece = nextPiece;
        nextPiece = createNewPiece();
        if (currentPiece.y === 0 && currentPiece.checkCollision()) {
            gameOver();
        }
    }

    draw(context, offsetX = 0, offsetY = 0) {
        this.coords.forEach(([x, y]) => {
            const pixelX = (this.x + x + offsetX) * BLOCK_SIZE;
            const pixelY = (this.y + y + offsetY) * BLOCK_SIZE;
            context.fillStyle = this.color;
            context.fillRect(pixelX, pixelY, BLOCK_SIZE - 1, BLOCK_SIZE - 1);
        });
    }
}

function createNewPiece() {
    const shapes = Object.keys(SHAPES);
    const randomShape = shapes[Math.floor(Math.random() * shapes.length)];
    return new Piece(randomShape);
}

function checkLines() {
    let linesCleared = 0;
    for (let y = GRID_HEIGHT - 1; y >= 0; y--) {
        if (grid[y].every(cell => cell !== null)) {
            grid.splice(y, 1);
            grid.unshift(Array(GRID_WIDTH).fill(null));
            linesCleared++;
            y++;
        }
    }
    if (linesCleared > 0) {
        lines += linesCleared;
        score += linesCleared * 100 * level;
        level = Math.floor(lines / 10) + 1;
        updateScore();
    }
}

function updateScore() {
    document.getElementById('score').textContent = score;
    document.getElementById('level').textContent = level;
    document.getElementById('lines').textContent = lines;
}

function draw() {
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    nextCtx.clearRect(0, 0, nextCanvas.width, nextCanvas.height);

    // 绘制网格中的方块
    for (let y = 0; y < GRID_HEIGHT; y++) {
        for (let x = 0; x < GRID_WIDTH; x++) {
            if (grid[y][x]) {
                ctx.fillStyle = grid[y][x];
                ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1);
            }
        }
    }

    // 绘制当前方块
    if (currentPiece) {
        currentPiece.draw(ctx);
    }

    // 绘制下一个方块
    if (nextPiece) {
        nextPiece.draw(nextCtx, 1, 1);
    }
}

function gameOver() {
    clearInterval(gameLoop);
    alert('游戏结束！得分：' + score);
    document.getElementById('startBtn').disabled = false;
}

function startGame() {
    // 重置游戏状态
    grid = Array(GRID_HEIGHT).fill().map(() => Array(GRID_WIDTH).fill(null));
    score = 0;
    level = 1;
    lines = 0;
    isPaused = false;
    updateScore();
    
    // 创建初始方块
    currentPiece = createNewPiece();
    nextPiece = createNewPiece();
    
    // 开始游戏循环
    if (gameLoop) clearInterval(gameLoop);
    gameLoop = setInterval(() => {
        if (!isPaused) {
            if (!currentPiece.moveDown()) {
                draw();
            }
            draw();
        }
    }, 1000 / level);

    document.getElementById('startBtn').disabled = true;
}

// 键盘控制
document.addEventListener('keydown', (event) => {
    if (!currentPiece || isPaused) return;

    switch (event.key) {
        case 'ArrowLeft':
            currentPiece.moveLeft();
            break;
        case 'ArrowRight':
            currentPiece.moveRight();
            break;
        case 'ArrowDown':
            currentPiece.moveDown();
            break;
        case 'ArrowUp':
            currentPiece.rotate();
            break;
        case ' ':
            isPaused = !isPaused;
            break;
    }
    draw();
});

// 开始按钮事件
document.getElementById('startBtn').addEventListener('click', startGame);

// 初始绘制
draw(); 