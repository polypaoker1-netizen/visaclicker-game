class ClickerGame {
    constructor() {
        this.visa = 63;
        this.level = 30;
        this.clickPower = 4;
        this.multiplier = 1;
        this.autoclickers = 0;
        this.inventory = [];
        this.currentFigure = 'circle';
        this.figures = ['circle', 'square', 'triangle'];
        this.giftChance = 0.01; // 1% шанс на появление подарка
        this.gifts = ['gift1.png', 'gift2.png', 'gift3.png'];
        
        this.init();
    }

    init() {
        this.updateDisplay();
        this.setupEventListeners();
        this.startGameLoop();
    }

    updateDisplay() {
        document.getElementById('visa').textContent = this.visa;
        document.getElementById('level').textContent = this.level;
        document.getElementById('click-power').textContent = `x${this.clickPower}`;
        document.getElementById('multiplier').textContent = `x${this.multiplier}`;
        document.getElementById('autoclickers').textContent = this.autoclickers;
    }

    setupEventListeners() {
        const figure = document.getElementById('figure');
        figure.addEventListener('click', () => this.handleClick());
        
        document.getElementById('menu-btn').addEventListener('click', () => this.openMenu());
        document.getElementById('inventory-btn').addEventListener('click', () => this.openInventory());
        document.getElementById('exit-btn').addEventListener('click', () => this.exitGame());
    }

    handleClick() {
        const points = this.clickPower * this.multiplier;
        this.visa += points;
        this.level++;
        this.updateDisplay();
        
        // Анимация клика
        const figure = document.getElementById('figure');
        figure.style.transform = 'scale(0.95)';
        setTimeout(() => {
            figure.style.transform = 'scale(1)';
        }, 100);
        
        // Проверка на выпадение подарка
        if (Math.random() < this.giftChance) {
            this.spawnGift();
        }
    }

    spawnGift() {
        const giftsArea = document.getElementById('gifts-area');
        const gift = document.createElement('img');
        const giftType = this.gifts[Math.floor(Math.random() * this.gifts.length)];
        
        gift.src = `assets/gifts/${giftType}`;
        gift.className = 'gift';
        gift.style.left = `${Math.random() * 80 + 10}%`;
        gift.style.top = `${Math.random() * 80 + 10}%`;
        
        gift.addEventListener('click', () => {
            this.collectGift(gift, giftType);
        });
        
        giftsArea.appendChild(gift);
        
        // Автоматическое исчезновение через 10 секунд
        setTimeout(() => {
            if (gift.parentNode) {
                gift.remove();
            }
        }, 10000);
    }

    collectGift(giftElement, giftType) {
        giftElement.remove();
        this.inventory.push(giftType);
        alert('🎁 Подарок получен!');
    }

    changeFigure() {
        this.currentFigure = this.figures[Math.floor(Math.random() * this.figures.length)];
        const figure = document.getElementById('figure');
        
        // Удаляем все классы фигур
        figure.classList.remove('circle', 'square', 'triangle');
        
        // Добавляем новый класс
        figure.classList.add(this.currentFigure);
    }

    startGameLoop() {
        // Смена фигуры каждые 2 секунды
        setInterval(() => {
            this.changeFigure();
        }, 2000);
        
        // Автокликеры
        setInterval(() => {
            if (this.autoclickers > 0) {
                this.visa += this.autoclickers * this.clickPower * this.multiplier;
                this.updateDisplay();
            }
        }, 1000);
    }

    openMenu() {
        Telegram.WebApp.openLink('menu.html');
    }

    openInventory() {
        Telegram.WebApp.openLink('inventory.html');
    }

    exitGame() {
        if (confirm('Выйти из игры?')) {
            Telegram.WebApp.close();
        }
    }
}

// Инициализация игры при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.game = new ClickerGame();
});