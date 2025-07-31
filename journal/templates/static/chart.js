// TODO: Plot volume as histogram on bottom and transactions overlay
class TradingChart {
    constructor(element, candleData = null, transactionData = null, options = {}) {
        this.theme = {
            background: options.background || '#ffffff',
            gridColor: options.gridColor || '#e0e0e0',
            textColor: options.textColor || '#333333',
            bullColor: options.bullColor || '#00ff41',
            bearColor: options.bearColor || '#ff4757',
            textFont: options.textFont || '12px Arial',
            padding: options.padding || 40,
            bottomPadding: options.bottomPadding || 60,
            startReplay: options.startReplay || new Date().toISOString(),
            ...options.theme
        };
        this.intializeCanvas(element);
        this.dailyCanvas = document.getElementById('dailyChart');
        this.intradayCanvas = document.getElementById('intradayChart');
        this.dailyCtx = this.dailyCanvas.getContext('2d');
        this.intradayCtx = this.intradayCanvas.getContext('2d');
        
        this.isPlaying = false;
        this.currentTime = new Date();
        this.speed = 1;
        this.replayInterval = null;
        
        this.dailyZoom = 1;
        this.intradayZoom = 1;

        if (candleData && candleData['1d']) {
            const dailyLength = candleData['1d'].length;
            this.dailyViewStart = Math.max(0, dailyLength - 31);
            this.dailyViewEnd = dailyLength;
        } else {
            this.dailyViewStart = 0;
            this.dailyViewEnd = 30;
        }

        if (candleData && candleData['1m']) {
            const intradayLength = candleData['1m'].length;
            this.intradayViewStart = Math.max(0, intradayLength - 60);
            this.intradayViewEnd = intradayLength;
        } else {
            this.intradayViewStart = 0;
            this.intradayViewEnd = 60;
        }
            
        this.tooltip = null;
        this.createTooltip();
        
        this.setupCanvas();
        
        // Cargar datos si se proporcionan, sino generar datos de ejemplo
        if (candleData) {
            this.loadData(candleData, transactionData);
        } else {
            this.generateData();
        }
        
        this.setupEventHandlers();
        this.drawCharts();

        // Configure responsive
        window.addEventListener('resize', () => {
            this.setupCanvas();
            this.drawCharts();
        });

        // Add keyboard controls
        document.addEventListener('keydown', (e) => {
            switch(e.code) {
                case 'Space':
                    e.preventDefault();
                    if (this.isPlaying) {
                        this.pause();
                    } else {
                        this.play();
                    }
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextStep();
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.stop();
                    break;
                case 'KeyR':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.reset();
                    }
                    break;
            }
        });
    }

    intializeCanvas(element) {
        let div = document.createElement('div');
        div.id = `trading-charts-${document.querySelectorAll('[id^="trading-charts-"]').length + 1}`;
        div.innerHTML = `
        <h4 class="">Daily Chart</h4>
        <div class="zoom-controls daily-controls">
            <button class="zoom-btn zoom-in"> <i class="fas fa-search-plus"></i> </button>
            <button class="zoom-btn zoom-out"> <i class="fas fa-search-minus"></i> </button>
        </div>
        <canvas id="dailyChart" width="800" height="300"></canvas>
        <div class="loading-spinner" id="dailySpinner">
            <div class="spinner-border" role="status"></div>
        </div>

        <h4 class="">Intraday Chart (1m)</h4>
        <div class="zoom-controls intraday-controls">
            <button class="zoom-btn zoom-in"> <i class="fas fa-search-plus"></i> </button>
            <button class="zoom-btn zoom-out"> <i class="fas fa-search-minus"></i> </button>
        </div>
        <canvas id="intradayChart" width="800" height="300"></canvas>
        <div class="loading-spinner" id="intradaySpinner">
            <div class="spinner-border" role="status"></div>
        </div>
        `
        div.querySelector('.daily-controls .zoom-btn.zoom-in').addEventListener('click', () => {
            this.zoomChart('daily', 1.2)
        });
        div.querySelector('.daily-controls .zoom-btn.zoom-out').addEventListener('click', () => {
            this.zoomChart('daily', 0.8)
        });
        div.querySelector('.intraday-controls .zoom-btn.zoom-in').addEventListener('click', () => {
            this.zoomChart('intraday', 1.2)
        });
        div.querySelector('.intraday-controls .zoom-btn.zoom-out').addEventListener('click', () => {
            this.zoomChart('intraday', 0.8)
        });
        element.appendChild(div);
    }

    setupCanvas() {
        // Ajustar canvas para alta resolución
        const ratio = window.devicePixelRatio || 1;
        [this.dailyCanvas, this.intradayCanvas].forEach(canvas => {
            const container = canvas.parentElement;
            canvas.style.width = '100%';
            canvas.style.height = '300px';

            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * ratio;
            canvas.height = rect.height * ratio;

            canvas.getContext('2d').scale(ratio, ratio);
            this.setupInteractive(canvas);
        });
    }

    loadData (candleData, transactionData) {


        // Generar transacciones de ejemplo basadas en los datos reales
        this.transactions = [];
        this.allTransactions = [];

        if (transactionData) {
            this.allTransactions = transactionData.map(transaction => ({
                time: new Date(`${transaction.date} ${transaction.time}+00:00`),
                type: transaction.type,
                price: transaction.price,
                quantity: transaction.quantity,
                commission: transaction.commission,
                id: transaction.id
            }));
            console.log(this.allTransactions);
            this.allTransactions.sort((a, b) => a.time - b.time);
        }

        // Cargar datos de velas diarias
        this.dailyData = [];
        if (candleData && candleData['1d']) {
            this.dailyData = candleData['1d'].map(candle => ({
                date: new Date(candle.date),
                open: candle.open,
                high: candle.high,
                low: candle.low,
                close: candle.close,
                volume: candle.volume || 0,
                session: candle.session,
                id: candle.id
            }));
        }

        // Cargar datos intradía (1 minuto)
        this.intradayData = [];
        this.allIntradayData = [];
        
        if (candleData && candleData['1m']) {
            this.allIntradayData = candleData['1m'].map(candle => ({
                time: new Date(candle.date),
                open: candle.open,
                high: candle.high,
                low: candle.low,
                close: candle.close,
                volume: candle.volume || 0,
                session: candle.session,
                id: candle.id
            }));

            this.allIntradayData.sort((a, b) => a.time - b.time);
            const intradayLength = this.allIntradayData.length;

            if (this.allTransactions.length > 0) {
                let indexes = this.allIntradayData
                                        .map((v, i) => ({ v, i })) // guardar también el índice
                                        .filter(item => {
                                            const candleDate = item.v.time;
                                            const transactionDate = this.allTransactions[0].time;
                                            return candleDate.getUTCFullYear() === transactionDate.getUTCFullYear() &&
                                                candleDate.getUTCMonth() === transactionDate.getUTCMonth() &&
                                                candleDate.getUTCDate() === transactionDate.getUTCDate();
                                        }).map(item => item.i);
                this.intradayViewStart = Math.max(0, indexes[0]);
                this.intradayViewEnd = Math.min(indexes[indexes.length-1], intradayLength);
            } else {
                this.intradayViewStart = Math.max(0, intradayLength - 60);
                this.intradayViewEnd = intradayLength;
            }
        }

        // Establecer tiempo inicial basado en los datos
        if (this.allIntradayData.length > 0) {
            this.currentTime = new Date(this.theme.startReplay) || new Date(this.allIntradayData[0].time);
            document.getElementById('startTime').value =
                this.currentTime.toISOString().slice(0, 16);
        }
    }

    generateData() {
        // Método de fallback para generar datos de ejemplo si no se proporcionan datos reales
        console.warn('No se proporcionaron datos reales, generando datos de ejemplo...');
        
        // Generar datos de velas diarias
        this.dailyData = [];
        let basePrice = 2.5;
        
        for (let i = 0; i < 30; i++) {
            const date = new Date('2024-07-01');
            date.setDate(date.getDate() + i);
            
            const open = basePrice + (Math.random() - 0.5) * 0.2;
            const close = open + (Math.random() - 0.5) * 0.3;
            const high = Math.max(open, close) + Math.random() * 0.1;
            const low = Math.min(open, close) - Math.random() * 0.1;
            
            this.dailyData.push({
                date: date,
                open: open,
                high: high,
                low: low,
                close: close,
                volume: Math.floor(Math.random() * 1000000) + 500000,
                id: i + 1
            });
            
            basePrice = close;
        }

        // Generar datos intradía (1 minuto)
        this.intradayData = [];
        this.allIntradayData = [];
        
        basePrice = 2.5;
        const startDate = new Date('2024-07-30T09:30:00');
        
        for (let i = 0; i < 390; i++) { // 6.5 horas * 60 minutos
            const time = new Date(startDate.getTime() + i * 60000);
            
            const open = basePrice + (Math.random() - 0.5) * 0.05;
            const close = open + (Math.random() - 0.5) * 0.1;
            const high = Math.max(open, close) + Math.random() * 0.02;
            const low = Math.min(open, close) - Math.random() * 0.02;
            
            const candle = {
                time: time,
                open: open,
                high: high,
                low: low,
                close: close,
                volume: Math.floor(Math.random() * 10000) + 1000,
                id: i + 1
            };
            
            this.allIntradayData.push(candle);
            basePrice = close;
        }
        this.intradayViewEnd = Math.min(60, this.allIntradayData.length);

        // Generar transacciones
        this.transactions = [];
        this.allTransactions = [];
        
        for (let i = 0; i < 20; i++) {
            const randomIndex = Math.floor(Math.random() * this.allIntradayData.length);
            const candle = this.allIntradayData[randomIndex];
            
            const transaction = {
                time: candle.time,
                type: Math.random() > 0.5 ? 'buy' : 'sell',
                price: candle.close + (Math.random() - 0.5) * 0.05,
                quantity: Math.floor(Math.random() * 1000) + 100,
                id: i + 1
            };
            
            this.allTransactions.push(transaction);
        }
        
        this.allTransactions.sort((a, b) => a.time - b.time);
    }

    setupEventHandlers() {
        document.getElementById('playBtn').addEventListener('click', () => this.play());
        document.getElementById('pauseBtn').addEventListener('click', () => this.pause());
        document.getElementById('stopBtn').addEventListener('click', () => this.stop());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('resetBtn').addEventListener('click', () => this.reset());
        
        const speedSlider = document.getElementById('speedSlider');
        speedSlider.addEventListener('input', (e) => {
            this.speed = parseInt(e.target.value);
            document.getElementById('speedValue').textContent = `${this.speed}x`;
            if (this.isPlaying) {
                this.pause();
                this.play();
            }
        });

        const startTimeInput = document.getElementById('startTime');
        startTimeInput.addEventListener('change', (e) => {
            this.currentTime = new Date(e.target.value);
        });
    }

    setupInteractive(canvas) {
        let isDragging = false;
        let lastX = 0;
        const chartType = canvas === this.dailyCanvas ? 'daily' : 'intraday';

        canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            lastX = e.clientX;
            canvas.style.cursor = 'grabbing';
            this.tooltip.style.display = 'none';
        });

        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            if (isDragging) {
                const deltaX = e.clientX - lastX;
                lastX = e.clientX;
                this.panChart(chartType, deltaX);
            } else {
                this.showTooltip(e, x, y, chartType);
            }
        });

        canvas.addEventListener('mouseup', () => {
            isDragging = false;
            canvas.style.cursor = 'default';
        });

        canvas.addEventListener('mouseleave', () => {
            isDragging = false;
            canvas.style.cursor = 'default';
            this.tooltip.style.display = 'none';
        });

        // Zoom con rueda del ratón
        canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const factor = e.deltaY > 0 ? 0.9 : 1.1;
            this.zoomChart(chartType, factor, x);
        });
    }

    createTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'trading-tooltip';
        this.tooltip.style.cssText = `
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            display: none;
        `;
        document.body.appendChild(this.tooltip);
    }

    panChart(chartType, deltaX) {
        const data = chartType === 'daily' ? this.dailyData : this.allIntradayData;
        if (data.length === 0) return;
        
        const rect = (chartType === 'daily' ? this.dailyCanvas : this.intradayCanvas).getBoundingClientRect();
        const chartWidth = rect.width - this.theme.padding;
        const zoom = chartType === 'daily' ? this.dailyZoom : this.intradayZoom;
        const visibleCandles = Math.floor(chartWidth / (8 * zoom)); // Mínimo 8px por vela
        
        // Calcular cuántas velas mover basado en el deltaX
        const candlesPerPixel = visibleCandles / chartWidth;
        const candlesToMove = Math.round(-deltaX * candlesPerPixel);
        
        if (chartType === 'daily') {
            this.dailyViewStart = Math.max(0, Math.min(data.length - visibleCandles, this.dailyViewStart + candlesToMove));
            this.dailyViewEnd = this.dailyViewStart + visibleCandles;
        } else {
            this.intradayViewStart = Math.max(0, Math.min(data.length - visibleCandles, this.intradayViewStart + candlesToMove));
            this.intradayViewEnd = this.intradayViewStart + visibleCandles;
        }
        
        this.drawCharts();
    }
    
    zoomChart(chartType, factor, mouseX = null) {
        const data = chartType === 'daily' ? this.dailyData : this.allIntradayData;
        if (data.length === 0) return;
        
        const rect = (chartType === 'daily' ? this.dailyCanvas : this.intradayCanvas).getBoundingClientRect();
        const chartWidth = rect.width - this.theme.padding;
        
        let currentViewStart, currentViewEnd, currentZoom;
        
        if (chartType === 'daily') {
            currentViewStart = this.dailyViewStart;
            currentViewEnd = this.dailyViewEnd;
            currentZoom = this.dailyZoom;
        } else {
            currentViewStart = this.intradayViewStart;
            currentViewEnd = this.intradayViewEnd;
            currentZoom = this.intradayZoom;
        }
        
        const newZoom = Math.max(0.1, Math.min(10, currentZoom * factor));
        const visibleCandles = Math.max(5, Math.floor(chartWidth / (8 * newZoom)));
        
        // Si se proporciona mouseX, hacer zoom hacia ese punto
        if (mouseX !== null) {
            const mouseRatio = (mouseX - this.theme.padding) / chartWidth;
            const centerIndex = currentViewStart + (currentViewEnd - currentViewStart) * mouseRatio;
            const newStart = Math.max(0, Math.min(data.length - visibleCandles, Math.floor(centerIndex - visibleCandles * mouseRatio)));
            const newEnd = newStart + visibleCandles;
            
            if (chartType === 'daily') {
                this.dailyZoom = newZoom;
                this.dailyViewStart = newStart;
                this.dailyViewEnd = newEnd;
            } else {
                this.intradayZoom = newZoom;
                this.intradayViewStart = newStart;
                this.intradayViewEnd = newEnd;
            }
        } else {
            // Zoom centrado
            const center = (currentViewStart + currentViewEnd) / 2;
            const newStart = Math.max(0, Math.min(data.length - visibleCandles, Math.floor(center - visibleCandles / 2)));
            const newEnd = newStart + visibleCandles;
            
            if (chartType === 'daily') {
                this.dailyZoom = newZoom;
                this.dailyViewStart = newStart;
                this.dailyViewEnd = newEnd;
            } else {
                this.intradayZoom = newZoom;
                this.intradayViewStart = newStart;
                this.intradayViewEnd = newEnd;
            }
        }
        
        this.drawCharts();
    }

    play() {
        if (this.isPlaying) return;
        
        this.isPlaying = true;
        document.getElementById('playBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;

        const start_date = new Date(document.getElementById('startTime').value);
        const todayCandles = this.dailyData.filter(candle => {
            const candleDate = candle.date;
            return candleDate.getTime() <= start_date.getTime();
        });
        this.drawDailyChart(todayCandles);

        this.intradayData = [];
        this.transactions = []; // Resetear transacciones para replay
        this.drawIntradayChart([]);
        
        this.replayInterval = setInterval(() => {
            this.nextStep();
        }, 1000 / this.speed);
    }

    pause() {
        this.isPlaying = false;
        document.getElementById('playBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        
        if (this.replayInterval) {
            clearInterval(this.replayInterval);
            this.replayInterval = null;
        }
        this.drawCharts();
    }

    stop() {
        this.pause();
        document.getElementById('stopBtn').disabled = true;
        this.reset();
    }

    reset() {
        this.currentTime = new Date(document.getElementById('startTime').value);
        this.intradayData = []; //.slice(0, 60);
        this.transactions = [];
        this.drawCharts();
    }

    nextStep() {
        // Avanzar 1 minuto
        this.currentTime.setMinutes(this.currentTime.getMinutes() + 1);
        
        // Agregar nueva vela intradía si existe
        const newCandle = this.allIntradayData.find(candle => 
            Math.abs(candle.time - this.currentTime) < 30000
        );
        
        if (newCandle && !this.intradayData.find(c => c.time.getTime() === newCandle.time.getTime())) {
            this.intradayData.push(newCandle);
            
            // Mantener solo las últimas 60 velas en vista
            if (this.intradayData.length > 60) {
                this.intradayData.shift();
            }
        }

        // Agregar transacciones que correspondan a este momento
        const newTransactions = this.allTransactions.filter(transaction =>
            Math.abs(transaction.time - this.currentTime) < 30000 &&
            !this.transactions.find(t => t.id === transaction.id)
        );
        
        this.transactions.push(...newTransactions);

        this.drawCharts();
        this.updateTransactionsList();

        // Verificar si hemos llegado al final
        const endTime = this.allIntradayData.length > 0 ? 
            new Date(this.allIntradayData[this.allIntradayData.length - 1].time) :
            new Date();
            
        if (this.currentTime >= endTime) {
            this.pause();
            document.getElementById('stopBtn').disabled = true;
        }
    }

    drawCharts() {
        this.drawDailyChart();
        this.drawIntradayChart();
    }
    
    showTooltip(e, x, y, chartType) {
        const allData = chartType === 'daily' ? this.dailyData : this.allIntradayData;
        const viewStart = chartType === 'daily' ? this.dailyViewStart : this.intradayViewStart;
        const viewEnd = chartType === 'daily' ? this.dailyViewEnd : this.intradayViewEnd;
        
        if (allData.length === 0) return;
        
        const visibleData = allData.slice(viewStart, viewEnd);
        if (visibleData.length === 0) return;
        
        const rect = (chartType === 'daily' ? this.dailyCanvas : this.intradayCanvas).getBoundingClientRect();
        const padding = this.theme.padding;
        const chartWidth = rect.width - padding;
        const spacing = chartWidth / visibleData.length;
        
        // Calcular índice de la vela
        const adjustedX = x - padding;
        const index = Math.floor(adjustedX / spacing);
        
        if (index >= 0 && index < visibleData.length) {
            const candle = visibleData[index];
            const date = candle.date || candle.time;
            
            this.tooltip.innerHTML = `
                <div><strong>${date.toLocaleDateString()} ${date.toLocaleTimeString()}</strong></div>
                <div>Open: ${candle.open.toFixed(2)}</div>
                <div>High: ${candle.high.toFixed(2)}</div>
                <div>Low: ${candle.low.toFixed(2)}</div>
                <div>Close: ${candle.close.toFixed(2)}</div>
                <div>Volume: ${candle.volume?.toLocaleString() || 'N/A'}</div>
            `;
            
            this.tooltip.style.display = 'block';
            this.tooltip.style.left = e.pageX + 10 + 'px';
            this.tooltip.style.top = e.pageY - 10 + 'px';
        } else {
            this.tooltip.style.display = 'none';
        }
    }

    drawDailyChart(data=null) {
        const ctx = this.dailyCtx;
        const canvas = this.dailyCanvas;
        const rect = canvas.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;

        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = this.theme.background;
        ctx.fillRect(0, 0, width, height);

        let visibleData;
        if (data != null) {
            visibleData = data.slice(this.dailyViewStart, this.dailyViewEnd);
        }
        else {
            visibleData = this.dailyData.slice(this.dailyViewStart, this.dailyViewEnd);
        }

        if (visibleData.length === 0) return;

        const padding = this.theme.padding;
        const bottomPadding = this.theme.bottomPadding;
        const chartWidth = width - padding;
        const chartHeight = height - 2 * padding;

        // Calcular rangos
        const prices = visibleData.flatMap(d => [d.high, d.low]);
        const minPrice = Math.min(...prices) * 0.99;
        const maxPrice = Math.max(...prices) * 1.01;

        const candleWidth = Math.max(2, (chartWidth / visibleData.length) * 0.8);
        const spacing = chartWidth / visibleData.length;

        // Dibujar grid
        this.drawGrid(ctx, padding, chartWidth, height - bottomPadding + 10 - padding, minPrice, maxPrice, bottomPadding);
        this.drawTimeAxis(ctx, padding, chartWidth, height - bottomPadding + 10, visibleData, spacing);

        // Dibujar velas
        visibleData.forEach((candle, index) => {
            this.printCandle(ctx, index, padding, spacing, candle.open, candle.high, candle.low, candle.close, maxPrice, minPrice, candleWidth, chartHeight, false);
        });

        this.drawTransactions(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, 'daily', visibleData);

        // Actualizar la última vela diaria basada en el tiempo actual
        this.updateLastDailyCandle(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, candleWidth);
    }

    drawIntradayChart(data=null) {
        const ctx = this.intradayCtx;
        const canvas = this.intradayCanvas;
        const rect = canvas.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;

        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = this.theme.background;
        ctx.fillRect(0, 0, width, height);

        let visibleData;
        if (data !== null && data.length > 0) {
            visibleData = data;
        } else if (this.isPlaying) {
            visibleData = this.intradayData;
        } else {
            // Mostrar datos basados en la vista actual
            visibleData = this.allIntradayData.slice(this.intradayViewStart, this.intradayViewEnd + 1);
        }

        if (visibleData.length === 0) return;

        const padding = this.theme.padding;
        const bottomPadding = this.theme.bottomPadding;
        const chartWidth = width - padding;
        const chartHeight = height - 2 * padding;

        // Calcular rangos
        const prices = visibleData.flatMap(d => [d.high, d.low]);
        const minPrice = Math.min(...prices) * 0.99;
        const maxPrice = Math.max(...prices) * 1.01;

        const candleWidth = Math.max(2, (chartWidth / visibleData.length) * 0.8);
        const spacing = chartWidth / visibleData.length;

        const maxVolume = Math.max(...visibleData.map(d => d.volume || 0));

        // Dibujar grid
        this.drawGrid(ctx, padding, chartWidth, height - bottomPadding + 10 - padding, minPrice, maxPrice, bottomPadding);
        this.drawTimeAxis(ctx, padding, chartWidth, height - bottomPadding + 10, visibleData, spacing);

        // Dibujar velas
        visibleData.forEach((candle, index) => {
            this.printVolume(ctx, index, padding, spacing, candle.volume, maxVolume, candleWidth, chartHeight, candle.close >= candle.open);
            // Dibujar la vela encima
            this.printCandle(ctx, index, padding, spacing, candle.open, candle.high, candle.low, candle.close, maxPrice, minPrice, candleWidth, chartHeight, candle.session, false);
        });

        // Dibujar transacciones
        this.drawTransactions(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, 'intraday', visibleData);
    }

    drawGrid(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice) {
        ctx.strokeStyle = this.theme.gridColor;
        ctx.lineWidth = 1;
        ctx.setLineDash([2, 2]);

        // Líneas horizontales
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(padding + chartWidth, y);
            ctx.stroke();

            // Etiquetas de precio
            if (maxPrice > minPrice) {
                const price = maxPrice - (maxPrice - minPrice) * (i / 5);
                ctx.fillStyle = this.theme.textColor;
                ctx.font = this.theme.textFont;
                ctx.textAlign = 'right';
                ctx.fillText(price.toFixed(2), padding - 5, y + 4);
            }
        }

        ctx.setLineDash([]);
    }
    
    drawTimeAxis(ctx, padding, chartWidth, y, data, spacing) {
        ctx.strokeStyle = this.theme.gridColor;
        ctx.fillStyle = this.theme.textColor;
        ctx.font = this.theme.textFont;
        ctx.textAlign = 'center';
        
        // Línea del eje
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(padding + chartWidth, y);
        ctx.stroke();
        
        // Etiquetas de tiempo
        const maxLabels = 8;
        const step = Math.max(1, Math.floor(data.length / maxLabels));
        
        for (let i = 0; i < data.length; i += step) {
            const x = padding + i * spacing + spacing / 2;
            const date = data[i].date || data[i].time;
            const label = date.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' });
            
            ctx.fillText(label, x, y + 20);
            
            // Marca en el eje
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x, y + 5);
            ctx.stroke();
        }
    }

    drawTransactions(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, chartType, visibleData = null) {
        if (!this.allTransactions || this.allTransactions.length === 0) {
            console.log('No hay transacciones para mostrar:', this.allTransactions);
            return;
        }

        console.log(`Dibujando transacciones en ${chartType}:`, this.allTransactions.length);

        // Obtener datos correctos según el contexto
        let dataToCheck;
        if (chartType === 'intraday') {
            if (this.isPlaying && this.intradayData.length > 0) {
                dataToCheck = this.intradayData;
            } else if (visibleData && visibleData.length > 0) {
                dataToCheck = visibleData;
            } else {
                dataToCheck = this.allIntradayData.slice(this.intradayViewStart, this.intradayViewEnd);
            }
        } else {
            if (visibleData && visibleData.length > 0) {
                dataToCheck = visibleData;
            } else {
                dataToCheck = this.dailyData.slice(this.dailyViewStart, this.dailyViewEnd);
            }
        }

        console.log(`Datos a verificar (${chartType}):`, dataToCheck.length);

        if (!dataToCheck || dataToCheck.length === 0) {
            console.log('No hay datos para verificar transacciones');
            return;
        }

        let transactionsDrawn = 0;
        this.allTransactions.forEach(transaction => {
            let index = -1;

            console.log(`Procesando transacción ${transaction.index}:`, {
                time: transaction.time,
                type: transaction.type,
                price: transaction.price
            });

            if (chartType === 'intraday') {
                // Buscar por tiempo (con tolerancia de 30 segundos)
                index = dataToCheck.findIndex(candle => 
                    Math.abs(candle.time - transaction.time) < 30000
                );
                console.log(`Búsqueda intraday - índice encontrado: ${index}`);
            } else {
                // Para gráfico diario, buscar por fecha
                index = dataToCheck.findIndex(candle => {
                    const candleDate = new Date(candle.date);
                    const transactionDate = transaction.time;
                    console.log(`Comparando fechas - Candle: ${candleDate.toDateString()}, Transaction: ${transactionDate.toDateString()}`);
                    return candleDate.getUTCFullYear() === transactionDate.getUTCFullYear() &&
                        candleDate.getUTCMonth() === transactionDate.getUTCMonth() &&
                        candleDate.getUTCDate() === transactionDate.getUTCDate();
                });
                console.log(`Búsqueda diaria - índice encontrado: ${index}`);
            }

            if (index === -1) {
                console.log('Transacción no encontrada en datos visibles');
                return;
            }
            
            // Calcular posición
            const x = padding + index * spacing + spacing / 2;
            const y = padding + (maxPrice - transaction.price) / (maxPrice - minPrice) * chartHeight;

            console.log(`Posición calculada - x: ${x}, y: ${y}`);

            // Verificar que las coordenadas estén dentro del canvas
            if (x < padding || x > padding + chartWidth || y < padding || y > padding + chartHeight) {
                console.log('Transacción fuera del área visible del canvas');
                return;
            }
            
            const isLong = transaction.type.toLowerCase() === 'long';
            const color = isLong ? '#00ff41' : '#ff4757';
            const triangleSize = 8;
            // Dibujar círculo de fondo
            ctx.fillStyle = color;
            ctx.beginPath();

            if (isLong) {
                // Triángulo hacia arriba para long
                ctx.moveTo(x, y - triangleSize);              // Punta arriba
                ctx.lineTo(x - triangleSize, y + triangleSize / 2);  // Izquierda abajo
                ctx.lineTo(x + triangleSize, y + triangleSize / 2);  // Derecha abajo
            } else {
                // Triángulo hacia abajo para short
                ctx.moveTo(x, y + triangleSize);              // Punta abajo
                ctx.lineTo(x - triangleSize, y - triangleSize / 2);  // Izquierda arriba
                ctx.lineTo(x + triangleSize, y - triangleSize / 2);  // Derecha arriba
            }

            ctx.closePath();
            ctx.fill();
    
            // Borde blanco
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();
    
            if (false) {
                // Texto de la transacción
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 10px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(
                    transaction.type.toLowerCase() === 'long' ? 'B' : 'S',
                    x,
                    y
                );

                // Etiqueta con precio (opcional, arriba del marcador)
                ctx.fillStyle = color;
                ctx.font = '9px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(
                    transaction.price.toFixed(2),
                    x,
                    y - 15
                );
            }

            transactionsDrawn++;
            console.log(`Transacción ${transaction.index} dibujada exitosamente`);
        });
    }

    updateLastDailyCandle(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, candleWidth) {
        // Encontrar velas intradía del día actual
        const todayCandles = this.intradayData.filter(candle => {
            const candleDate = candle.time;
            const currentDate = new Date(this.currentTime);
            return candleDate.getUTCFullYear() === currentDate.getUTCFullYear() &&
                    candleDate.getUTCMonth() === currentDate.getUTCMonth() &&
                    candleDate.getUTCDate() === currentDate.getUTCDate();
        });

        if (todayCandles.length === 0) return;

        // Calcular OHLC para el día actual
        const dayOpen = todayCandles[0].open;
        const dayClose = todayCandles[todayCandles.length - 1].close;
        const dayHigh = Math.max(...todayCandles.map(c => c.high));
        const dayLow = Math.min(...todayCandles.map(c => c.low));

        // Actualizar la última vela diaria
        const lastIndex = this.dailyData.length - 1;

        
        const start_date = new Date(document.getElementById('startTime').value);
        const pastCandles = this.dailyData.filter(candle => {
            const candleDate = new Date(candle.date);
            return candleDate.getTime() <= start_date.getTime();
        });
        console.log(pastCandles);
        if (pastCandles.length - 1 >= 0) {
            this.printCandle(ctx, lastIndex, padding, spacing, dayOpen, dayHigh, dayLow, dayClose, maxPrice, minPrice, candleWidth, chartHeight, true);
        }
    }

    printCandle(ctx, index, padding, spacing, open, high, low, close, maxPrice, minPrice, candleWidth, chartHeight, session='RH', reprint=false) {
        const x = padding + index * spacing + spacing / 2;
        const openY = padding + (maxPrice - open) / (maxPrice - minPrice) * chartHeight;
        const closeY = padding + (maxPrice - close) / (maxPrice - minPrice) * chartHeight;
        const highY = padding + (maxPrice - high) / (maxPrice - minPrice) * chartHeight;
        const lowY = padding + (maxPrice - low) / (maxPrice - minPrice) * chartHeight;

        if (reprint) {
            this.deleteCandle(ctx, x, padding, candleWidth, chartHeight);
        }

        // Dibujar fondo según la sesión
        if (session === 'PM') {
            ctx.fillStyle = 'rgba(255, 165, 0, 0.1)'; // naranja claro
            ctx.fillRect(padding + index * spacing, padding, spacing, chartHeight);
        } else if (session === 'AH') {
            ctx.fillStyle = 'rgba(30, 64, 175, 0.1)'; // azul oscuro claro
            ctx.fillRect(padding + index * spacing, padding, spacing, chartHeight);
        }

        // Color según si es alcista o bajista
        const isGreen = close > open;
        ctx.fillStyle = isGreen ? this.theme.bullColor : this.theme.bearColor;
        ctx.strokeStyle = isGreen ? this.theme.bullColor : this.theme.bearColor;

        // Línea alta-baja
        ctx.beginPath();
        ctx.moveTo(x, highY);
        ctx.lineTo(x, lowY);
        ctx.lineWidth = 1;
        ctx.stroke();

        // Cuerpo de la vela actualizada
        const bodyHeight = Math.abs(closeY - openY);
        ctx.fillRect(x - candleWidth/2, Math.min(openY, closeY), candleWidth, Math.max(2, bodyHeight));
    }

    printVolume (ctx, index, padding, spacing, volume, maxVolume, candleWidth, chartHeight, isUp,) {
        const x = padding + index * spacing + spacing / 2;
        const barWidth = candleWidth * 0.8;

        const volumeHeight = chartHeight * 0.2;
        const priceHeight = chartHeight - volumeHeight;

        volume = volume || 0;
        const volHeight = (volume / maxVolume) * volumeHeight;

        const y = padding + priceHeight + (volumeHeight - volHeight);

        // Color según si es alcista o bajista
        ctx.fillStyle = isUp ? this.theme.bullColor : this.theme.bearColor;

        ctx.fillRect(x - barWidth / 2, y, barWidth, volHeight);
    }
    
    deleteCandle(ctx, x, padding, candleWidth, chartHeight) {
        // Limpiar área de la última vela
        ctx.clearRect(x - candleWidth, padding, candleWidth * 2, chartHeight);

        // Redibujar fondo
        ctx.fillStyle = this.theme.background;
        ctx.fillRect(x - candleWidth, padding, candleWidth * 2, chartHeight);
    }

    updateTransactionsList() {
        const container = document.getElementById('transactionsList');
        container.innerHTML = '';

        // Mostrar las últimas 5 transacciones
        const recentTransactions = this.transactions.slice(-5).reverse();
        
        recentTransactions.forEach(transaction => {
            const transactionDiv = document.createElement('div');
            transactionDiv.className = `d-flex justify-content-between align-items-center p-2 mb-2 rounded ${
                transaction.type === 'buy' ? 'bg-success' : 'bg-danger'
            } bg-opacity-10 border border-${transaction.type === 'buy' ? 'success' : 'danger'}`;
            
            transactionDiv.innerHTML = `
                <div>
                    <i class="fas fa-${transaction.type === 'buy' ? 'arrow-up' : 'arrow-down'} me-2"></i>
                    <strong>${transaction.type.toUpperCase()}</strong>
                    <span class="ms-2">${transaction.quantity} acciones</span>
                </div>
                <div class="text-end">
                    <div class="fw-bold">${transaction.price.toFixed(2)}</div>
                    <small class="text-muted">${transaction.time.toLocaleTimeString('es-ES')}</small>
                </div>
            `;
            
            container.appendChild(transactionDiv);
        });

        if (recentTransactions.length === 0) {
            container.innerHTML = '<div class="text-muted text-center">No hay transacciones aún</div>';
        }
    }
}
