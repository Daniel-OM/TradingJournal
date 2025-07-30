
class TradingChart {
    constructor(candleData = null, transactionData = null) {
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
        
        this.setupCanvas();
        
        // Cargar datos si se proporcionan, sino generar datos de ejemplo
        if (candleData) {
            this.loadData(candleData, transactionData);
        } else {
            this.generateData();
        }
        
        this.setupEventHandlers();
        this.drawCharts();
    }

    setupCanvas() {
        // Ajustar canvas para alta resolución
        const ratio = window.devicePixelRatio || 1;
        [this.dailyCanvas, this.intradayCanvas].forEach(canvas => {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * ratio;
            canvas.height = rect.height * ratio;
            canvas.style.width = rect.width + 'px';
            canvas.style.height = rect.height + 'px';
            canvas.getContext('2d').scale(ratio, ratio);
        });
    }

    loadData(candleData, transactionData) {
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
                id: candle.id
            }));
            
            // Ordenar por fecha
            this.allIntradayData.sort((a, b) => a.time - b.time);
        }

        // Generar transacciones de ejemplo basadas en los datos reales
        this.transactions = [];
        this.allTransactions = [];
        
        if (transactionData) {
            this.allTransactions = transactionData.map(transaction => ({
                time: new Date(`${transaction.date}T${transaction.time}`),
                type: transaction.type,
                price: transaction.price,
                quantity: transaction.quantity,
                commission: transaction.commission,
                id: transaction.id
            }));
            
            this.allTransactions.sort((a, b) => a.time - b.time);
        }

        // Establecer tiempo inicial basado en los datos
        if (this.allIntradayData.length > 0) {
            this.currentTime = new Date(this.allIntradayData[0].time);
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
            this.updateDisplay();
        });
    }

    play() {
        if (this.isPlaying) return;
        
        this.isPlaying = true;
        document.getElementById('playBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;
        
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
    }

    stop() {
        this.pause();
        document.getElementById('stopBtn').disabled = true;
        this.reset();
    }

    reset() {
        this.currentTime = new Date(document.getElementById('startTime').value);
        this.intradayData = [];
        this.transactions = [];
        this.updateDisplay();
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

        this.updateDisplay();
        this.drawCharts();
        this.updateTransactionsList();

        // Verificar si hemos llegado al final
        const endTime = this.allIntradayData.length > 0 ? 
            new Date(this.allIntradayData[this.allIntradayData.length - 1].time) :
            new Date('2024-07-30T16:00:00');
            
        if (this.currentTime >= endTime) {
            this.pause();
            document.getElementById('stopBtn').disabled = true;
        }
    }

    updateDisplay() {
        document.getElementById('currentTime').textContent = 
            this.currentTime.toLocaleString('es-ES');
    }

    drawCharts() {
        this.drawDailyChart();
        this.drawIntradayChart();
    }

    drawDailyChart() {
        const ctx = this.dailyCtx;
        const canvas = this.dailyCanvas;
        const width = canvas.width / window.devicePixelRatio;
        const height = canvas.height / window.devicePixelRatio;

        ctx.clearRect(0, 0, width, height);
        
        // Fondo
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, width, height);

        if (this.dailyData.length === 0) return;

        const padding = 40;
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;

        // Calcular rangos
        const prices = this.dailyData.flatMap(d => [d.high, d.low]);
        const minPrice = Math.min(...prices) * 0.99;
        const maxPrice = Math.max(...prices) * 1.01;

        const candleWidth = Math.max(8, (chartWidth / this.dailyData.length) * 0.8 * this.dailyZoom);
        const spacing = chartWidth / this.dailyData.length * this.dailyZoom;

        // Dibujar grid
        this.drawGrid(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice);

        // Dibujar velas
        this.dailyData.forEach((candle, index) => {
            const x = padding + index * spacing + spacing / 2;
            const openY = padding + (maxPrice - candle.open) / (maxPrice - minPrice) * chartHeight;
            const closeY = padding + (maxPrice - candle.close) / (maxPrice - minPrice) * chartHeight;
            const highY = padding + (maxPrice - candle.high) / (maxPrice - minPrice) * chartHeight;
            const lowY = padding + (maxPrice - candle.low) / (maxPrice - minPrice) * chartHeight;

            // Color según si es alcista o bajista
            const isGreen = candle.close > candle.open;
            ctx.fillStyle = isGreen ? '#00ff41' : '#ff4757';
            ctx.strokeStyle = isGreen ? '#00ff41' : '#ff4757';

            // Línea alta-baja
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.lineWidth = 1;
            ctx.stroke();

            // Cuerpo de la vela
            const bodyHeight = Math.abs(closeY - openY);
            ctx.fillRect(x - candleWidth/2, Math.min(openY, closeY), candleWidth, Math.max(2, bodyHeight));
        });

        // Actualizar la última vela diaria basada en el tiempo actual
        this.updateLastDailyCandle(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, candleWidth);
    }

    drawIntradayChart() {
        const ctx = this.intradayCtx;
        const canvas = this.intradayCanvas;
        const width = canvas.width / window.devicePixelRatio;
        const height = canvas.height / window.devicePixelRatio;

        ctx.clearRect(0, 0, width, height);
        
        // Fondo
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, width, height);

        if (this.intradayData.length === 0) return;

        const padding = 40;
        const chartWidth = width - 2 * padding;
        const chartHeight = height - 2 * padding;

        // Calcular rangos
        const prices = this.intradayData.flatMap(d => [d.high, d.low]);
        const minPrice = Math.min(...prices) * 0.999;
        const maxPrice = Math.max(...prices) * 1.001;

        const candleWidth = Math.max(4, (chartWidth / Math.max(60, this.intradayData.length)) * 0.8 * this.intradayZoom);
        const spacing = chartWidth / Math.max(60, this.intradayData.length) * this.intradayZoom;

        // Dibujar grid
        this.drawGrid(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice);

        // Dibujar velas
        this.intradayData.forEach((candle, index) => {
            const x = padding + index * spacing + spacing / 2;
            const openY = padding + (maxPrice - candle.open) / (maxPrice - minPrice) * chartHeight;
            const closeY = padding + (maxPrice - candle.close) / (maxPrice - minPrice) * chartHeight;
            const highY = padding + (maxPrice - candle.high) / (maxPrice - minPrice) * chartHeight;
            const lowY = padding + (maxPrice - candle.low) / (maxPrice - minPrice) * chartHeight;

            // Color según si es alcista o bajista
            const isGreen = candle.close > candle.open;
            ctx.fillStyle = isGreen ? '#00ff41' : '#ff4757';
            ctx.strokeStyle = isGreen ? '#00ff41' : '#ff4757';

            // Línea alta-baja
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.lineWidth = 1;
            ctx.stroke();

            // Cuerpo de la vela
            const bodyHeight = Math.abs(closeY - openY);
            ctx.fillRect(x - candleWidth/2, Math.min(openY, closeY), candleWidth, Math.max(1, bodyHeight));
        });

        // Dibujar transacciones
        this.drawTransactions(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, 'intraday');
    }

    drawGrid(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice) {
        ctx.strokeStyle = '#333';
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
                ctx.fillStyle = '#888';
                ctx.font = '12px Arial';
                ctx.textAlign = 'right';
                ctx.fillText(price.toFixed(2), padding - 5, y + 4);
            }
        }

        ctx.setLineDash([]);
    }

    drawTransactions(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, chartType) {
        this.transactions.forEach(transaction => {
            let x, y;
            
            if (chartType === 'intraday') {
                const index = this.intradayData.findIndex(candle => 
                    Math.abs(candle.time - transaction.time) < 30000
                );
                if (index === -1) return;
                
                x = padding + index * spacing + spacing / 2;
                y = padding + (maxPrice - transaction.price) / (maxPrice - minPrice) * chartHeight;
            }

            // Dibujar marcador de transacción
            ctx.fillStyle = transaction.type === 'buy' ? '#00ff41' : '#ff4757';
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, 2 * Math.PI);
            ctx.fill();

            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Etiqueta
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(
                transaction.type.toUpperCase(),
                x,
                y - 12
            );
        });
    }

    updateLastDailyCandle(ctx, padding, chartWidth, chartHeight, minPrice, maxPrice, spacing, candleWidth) {
        // Encontrar velas intradía del día actual
        const todayCandles = this.intradayData.filter(candle => {
            const candleDate = new Date(candle.time);
            const currentDate = new Date(this.currentTime);
            return candleDate.toDateString() === currentDate.toDateString();
        });

        if (todayCandles.length === 0) return;

        // Calcular OHLC para el día actual
        const dayOpen = todayCandles[0].open;
        const dayClose = todayCandles[todayCandles.length - 1].close;
        const dayHigh = Math.max(...todayCandles.map(c => c.high));
        const dayLow = Math.min(...todayCandles.map(c => c.low));

        // Actualizar la última vela diaria
        const lastIndex = this.dailyData.length - 1;
        if (lastIndex >= 0) {
            const x = padding + lastIndex * spacing + spacing / 2;
            const openY = padding + (maxPrice - dayOpen) / (maxPrice - minPrice) * chartHeight;
            const closeY = padding + (maxPrice - dayClose) / (maxPrice - minPrice) * chartHeight;
            const highY = padding + (maxPrice - dayHigh) / (maxPrice - minPrice) * chartHeight;
            const lowY = padding + (maxPrice - dayLow) / (maxPrice - minPrice) * chartHeight;

            // Limpiar área de la última vela
            ctx.clearRect(x - candleWidth, padding, candleWidth * 2, chartHeight);

            // Redibujar fondo
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(x - candleWidth, padding, candleWidth * 2, chartHeight);

            // Color según si es alcista o bajista
            const isGreen = dayClose > dayOpen;
            ctx.fillStyle = isGreen ? '#00ff41' : '#ff4757';
            ctx.strokeStyle = isGreen ? '#00ff41' : '#ff4757';

            // Línea alta-baja
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.lineWidth = 1;
            ctx.stroke();

            // Cuerpo de la vela actualizada
            const bodyHeight = Math.abs(closeY - openY);
            ctx.fillRect(x - candleWidth/2, Math.min(openY, closeY), candleWidth, Math.max(2, bodyHeight));

            // Efecto de brillo para indicar actualización
            ctx.shadowColor = isGreen ? '#00ff41' : '#ff4757';
            ctx.shadowBlur = 10;
            ctx.strokeRect(x - candleWidth/2, Math.min(openY, closeY), candleWidth, Math.max(2, bodyHeight));
            ctx.shadowBlur = 0;
        }
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
