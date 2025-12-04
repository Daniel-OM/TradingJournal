
class Charts {
    constructor(data, chartsCommonOptions=null, show_r=false) {
        this.data = data;
        this.show_r = show_r;

        Chart.defaults.color = '#b0b0b0';
        Chart.defaults.backgroundColor = '#2d2d2d';
        Chart.defaults.borderColor = '#404040';
        this.chartsCommonOptions = chartsCommonOptions || {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: '#b0b0b0' },
                    grid: { color: '#b0b0b0' }
                },
                y: {
                    ticks: { color: '#b0b0b0' },
                    grid: { color: '#b0b0b0' }
                }
            }
        };
        this.charts = {};
    }

    renderAll(data=null, show_r=false) {
        if (data) {
            this.data = data;
        }
        if (show_r) {
            this.show_r = show_r;
        }
        console.log('Rendering charts:', data);
        this.renderCharts();
        this.renderBestWorstSymbols();
    }
    
    async renderEquityChart() {

        if (this.charts.equity) {
            this.charts.equity.destroy();
        }
        const equityCtx = document.getElementById('equityChart');
        if (!equityCtx) return;
        this.charts.equity = new Chart(equityCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: this.data.equity_curve?.dates,
                datasets: [{
                    label: this.show_r ? 'Cumulative Rs' : 'Cumulative P&L',
                    data: this.data.equity_curve?.equity,
                    borderColor: '#007cff',
                    backgroundColor: 'rgba(0, 124, 255, 0.1)',
                    fill: true,
                    tension: 0.1,
                    yAxisID: 'y'
                }, {
                    label: 'DrawDown',
                    data: this.data.equity_curve?.drawdown,
                    borderColor: '#ff322d',
                    backgroundColor: 'rgba(255, 50, 45, 0.1)',
                    fill: true,
                    tension: 0.1,
                    yAxisID: 'y1'
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                scales: {
                    ...this.chartsCommonOptions.scales,
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#b0b0b0' },
                        grid: { drawOnChartArea: false }
                    }
                },
                plugins: {
                    ...this.chartsCommonOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return this.show_r ? 'Rs: ${context.parsed.y.toFixed(2)}' : `P&L: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    async renderPnlDistribution() {
        if (this.charts.pnlDist) {
            this.charts.pnlDist.destroy();
        }
        const pnlDistCtx = document.getElementById('pnlDistributionChart');
        if (!pnlDistCtx) return;
        this.charts.pnlDist = new Chart(pnlDistCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: this.data.pnl_distribution?.bins,
                datasets: [{
                    label: 'Trades',
                    data: this.data.pnl_distribution?.counts,
                    backgroundColor: function(context) {
                        const value = context.parsed?.x;
                        return value > 0 ? '#00c851' : value < 0 ? '#ff4444' : '#b0b0b0';
                    }
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
            }
        });
    }

    async renderDailyReturn() {
        if (this.charts.daily) {
            this.charts.daily.destroy();
        }
        const dailyCtx = document.getElementById('dailyPnlChart');
        if (!dailyCtx) return;
        this.charts.daily = new Chart(dailyCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: this.data.day_analysis?.days,
                datasets: [{
                    label: this.show_r ? 'Daily Rs' : 'Daily P&L',
                    data: this.data.day_analysis?.total_pnl,
                    backgroundColor: function(context) {
                        const value = context.parsed?.y;
                        return value > 0 ? '#00c851' : value < 0 ? '#ff4444' : '#b0b0b0';
                    }
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
            }
        });
    }

    async renderMonthlyReturn() {
        if (this.charts.monthly) {
            this.charts.monthly.destroy();
        }
        const monthlyCtx = document.getElementById('monthlyPnlChart');
        if (!monthlyCtx) return;
        this.charts.monthly = new Chart(monthlyCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: this.data.month_analysis?.months,
                datasets: [{
                    label: this.show_r ? 'Monthly Rs' : 'Monthly P&L',
                    data: this.data.month_analysis?.total_pnl,
                    backgroundColor: function(context) {
                        const value = context.parsed?.y;
                        return value > 0 ? '#00c851' : value < 0 ? '#ff4444' : '#b0b0b0';
                    }
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
            }
        });
    }

    async renderWeekdayExpectancy() {
        if (this.charts.weekday) {
            this.charts.weekday.destroy();
        }
        const weekdayCtx = document.getElementById('weekdayChart');
        if (!weekdayCtx) return;
        this.charts.weekday = new Chart(weekdayCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: this.data.weekday_analysis?.days,
                datasets: [{
                    label: 'Expectancy',
                    data: this.data.weekday_analysis?.expectancy,
                    backgroundColor: function(context) {
                        const value = context.parsed?.y;
                        return value > 0 ? '#00c851' : value < 0 ? '#ff4444' : '#b0b0b0';
                    }
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
            }
        });
    }

    async renderHourlyExpectancy() {
        if (this.charts.hourly) {
            this.charts.hourly.destroy();
        }
        const hourlyCtx = document.getElementById('hourlyChart');
        if (!hourlyCtx) return;
        this.charts.hourly = new Chart(hourlyCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: this.data.hour_analysis?.hours.map(h => new Date(`1970-01-01 ${h}:00+00:00`).toLocaleString([], { hour: '2-digit', minute: '2-digit' })),
                datasets: [{
                    label: 'Expectancy',
                    data: this.data.hour_analysis?.expectancy,
                    backgroundColor: function(context) {
                        const value = context.parsed?.y;
                        return value > 0 ? '#00c851' : value < 0 ? '#ff4444' : '#b0b0b0';
                    }
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
            }
        });
    }

    async renderSymbolPortion() {
        if (this.charts.symbol) {
            this.charts.symbol.destroy();
        }
        const symbolCtx = document.getElementById('symbolChart');
        if (!symbolCtx) return;
        this.charts.symbol = new Chart(symbolCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: this.data.symbol_performance?.symbols,
                datasets: [{
                    data: this.data.symbol_performance?.expectancy,
                    backgroundColor: [
                        '#007cff', '#00c851', '#ff4444', '#ffbb33', '#9c27b0',
                        '#e91e63', '#795548', '#607d8b', '#ff9800', '#4caf50'
                    ]
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                scales: {} // Remove scales for doughnut chart
            }
        });
    }    
    
    async renderHoldTime() {
        if (this.charts.holdTime) {
            this.charts.holdTime.destroy();
        }
        const holdTimeCtx = document.getElementById('holdTimeChart');
        if (!holdTimeCtx) return;
        this.charts.holdTime = new Chart(holdTimeCtx.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Trades', // TODO: Scatter without string x axis
                    data: this.data.hold_time_analysis?.hold_times.map((x, i) => ({ x: Math.round(x).toFixed(0) , y: this.data.hold_time_analysis?.pnl[i] })).sort((a, b) => Number(a.x) - Number(b.x)),
                    backgroundColor: function(context) {
                        const dataPoint = context.raw;
                        return dataPoint ? dataPoint.y > 0 ? '#00c851' : dataPoint.y < 0 ? '#ff4444' : '#b0b0b0' : '#b0b0b0';
                    },
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    ...this.chartsCommonOptions.scales,
                    x: {
                        ...this.chartsCommonOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Hold Time (hours)',
                            color: '#b0b0b0'
                        }
                    },
                    y: {
                        ...this.chartsCommonOptions.scales.y,
                        title: {
                            display: true,
                            text: this.show_r ? 'P&L (R)' : 'P&L ($)',
                            color: '#b0b0b0'
                        }
                    }
                }
            }
        });
    }

    async renderTradeSize() {
        if (this.charts.size) {
            this.charts.size.destroy();
        }
        const sizeCtx = document.getElementById('sizeAnalysisChart');
        if (!sizeCtx) return;
        this.charts.size = new Chart(sizeCtx.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Trades', // TODO: Scatter without string x axis
                    data: this.data.size_analysis?.sizes.map((x, i) => ({ x: Math.round(x).toFixed(0) , y: this.data.size_analysis?.pnl[i] })).sort((a, b) => Number(a.x) - Number(b.x)),
                    backgroundColor: function(context) {
                        const dataPoint = context.raw;
                        return dataPoint ? dataPoint.y > 0 ? '#00c851' : dataPoint.y < 0 ? '#ff4444' : '#b0b0b0' : '#b0b0b0';
                    },
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    ...this.chartsCommonOptions.scales,
                    x: {
                        ...this.chartsCommonOptions.scales.x,
                        title: {
                            display: true,
                            text: 'Position Size',
                            color: '#b0b0b0'
                        }
                    },
                    y: {
                        ...this.chartsCommonOptions.scales.y,
                        title: {
                            display: true,
                            text: this.show_r ? 'P&L (R)' : 'P&L ($)',
                            color: '#b0b0b0'
                        }
                    }
                }
            }
        });
    }

    async renderTradeSpeed() {
        if (this.charts.tradeSpeed) {
            this.charts.tradeSpeed.destroy();
        }
        const tradeSpeedCtx = document.getElementById('tradeSpeedChart');
        if (!tradeSpeedCtx) return;
        this.charts.tradeSpeed = new Chart(tradeSpeedCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: this.data.trade_speed?.trade_speed_pct.labels,
                datasets: [
                    {
                        'label': 'Straight Up',
                        'data': this.data.trade_speed?.trade_speed_pct.datasets.straight_up,
                        'borderColor': 'rgb(34, 197, 94)',
                        'backgroundColor': 'rgba(34, 197, 94, 0.2)',
                        'fill': true,
                        'tension': 0.1,
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Straight Down', 
                        'data': this.data.trade_speed?.trade_speed_pct.datasets.straight_dn,
                        'borderColor': 'rgb(239, 68, 68)',
                        'backgroundColor': 'rgba(239, 68, 68, 0.2)',
                        'fill': true,
                        'tension': 0.1,
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Finish Up',
                        'data': this.data.trade_speed?.trade_speed_pct.datasets.finish_up,
                        'borderColor': 'rgb(59, 130, 246)',
                        'backgroundColor': 'rgba(59, 130, 246, 0.2)',
                        'fill': true,
                        'tension': 0.1,
                        'yAxisID': 'y'
                    },
                    {
                        'label': 'Finish Down',
                        'data': this.data.trade_speed?.trade_speed_pct.datasets.finish_dn,
                        'borderColor': 'rgb(249, 115, 22)',
                        'backgroundColor': 'rgba(249, 115, 22, 0.2)',
                        'fill': true,
                        'tension': 0.1,
                        'yAxisID': 'y'
                    }
                ]
            },
            options: this.chartsCommonOptions
        });
    }

    async renderRiskReturnChart() {
        if (this.charts.riskReturn) {
            this.charts.riskReturn.destroy();
        }
        const ctx = document.getElementById('riskReturnChart');
        if (!ctx) return;
        
        this.charts.riskReturn = new Chart(ctx.getContext('2d'), {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Symbols',
                    data: this.data.risk_return_scatter?.map(d => ({
                        x: d.volatility,
                        y: d.return,
                        symbol: d.symbol
                    })),
                    backgroundColor: function(context) {
                        const dataPoint = context.raw;
                        return dataPoint ? dataPoint.y > 0 ? '#00c851' : dataPoint.y < 0 ? '#ff4444' : '#b0b0b0' : '#b0b0b0';
                    },
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                ...this.chartsCommonOptions,
                plugins: {
                    ...this.chartsCommonOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = context.raw;
                                return `${point.symbol}: ${point.y.toFixed(2)}% return, ${point.x.toFixed(2)}% volatility`;
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    ...this.chartsCommonOptions.scales,
                    x: {
                        title: {
                            display: true,
                            text: 'Volatility (%)',
                            color: '#b0b0b0'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Return (%)',
                            color: '#b0b0b0'
                        }
                    }
                }
            }
        });
    }

    async renderBestWorstSymbols() {
        const data = this.data.best_worst_symbols;
        if (!data || !data.best || !data.worst) return;

        const createSymbolRow = (symbol, isProfit) => {
            const rowClass = isProfit ? 'card-profit' : 'card-loss';
            console.log('symbol row:', symbol);
            return `
                <div class="card ${rowClass}">
                    <div class="card-body d-flex flex-row pt-1 pb-1">
                        <div class="fw-bold">${symbol.symbol}</div>
                        <div class="ms-auto me-auto">
                            <span class="text-muted">Total P&L:</span>
                            <span class="">${formatNumber(symbol.total_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}</span>
                        </div>
                        <div class="ms-auto me-auto">
                            <span class="text-muted">Exp.:</span>
                            <span class="">${formatNumber(symbol.expectancy, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}</span>
                        </div>
                    </div>
                </div>
            `;
        };

        // Renderizar mejores activos
        const bestContainer = document.getElementById('bestSymbolsList');
        if (bestContainer) {
            if (data.best && data.best.length > 0) {
                bestContainer.innerHTML = data.best.map(s => createSymbolRow(s, true)).join('');
            } else {
                bestContainer.innerHTML = '<div class="text-muted text-center py-4">No data available</div>';
            }
        }

        // Renderizar peores activos
        const worstContainer = document.getElementById('worstSymbolsList');
        if (worstContainer) {
            if (data.worst && data.worst.length > 0) {
                worstContainer.innerHTML = data.worst.map(s => createSymbolRow(s, false)).join('');
            } else {
                worstContainer.innerHTML = '<div class="text-muted text-center py-4">No data available</div>';
            }
        }
    }
    
}

class TradeCharts extends Charts {
    constructor(data, chartsCommonOptions=null, show_r=false) {
        super(data, chartsCommonOptions, show_r);
    }

    async renderCharts() {
        this.renderEquityChart();
        this.renderPnlDistribution();
        this.renderDailyReturn();
        this.renderMonthlyReturn();
        this.renderWeekdayExpectancy();
        this.renderHourlyExpectancy();
        this.renderSymbolPortion();
        this.renderHoldTime();
        this.renderTradeSize();
        this.renderTradeSpeed();
    }
}

class WatchlistCharts extends Charts {
    constructor(data, chartsCommonOptions=null, show_r=false) {
        super(data, chartsCommonOptions, show_r);
    }

    calculateRadius (value, min_value, max_value, min_radius = 3, max_radius = 15) {
        return max_value != min_value ? Math.max(Math.min(max_radius * (value - min_value) / (max_value - min_value), max_radius), min_radius) : max_radius;
    }

    async renderExecutionOptimization() {
        const chartData = this.data.execution_optimization;
        if (!chartData) return;

        if (this.charts.executionOptimization) {
            this.charts.executionOptimization.destroy();
        }

        const ctxExecution = document.getElementById("executionOptimizationChart");
        if (!ctxExecution) return;

        // --- Heatmap datasets ---
        const max_radius = 50;
        const min_radius = 5;
        const max_max = Math.max(...chartData.heatmap_max.map(h => h.count));
        const max_min = Math.min(...chartData.heatmap_max.map(h => h.count));
        const q_max = chartData.heatmap_max.reduce((sum, c) => { return sum + c.count; }, 0);
        const heatmapMaxDataset = {
            label: 'Maximums',
            type: 'bubble',
            xAxisID: 'xMain',
            yAxisID: 'yMain',
            data: chartData.heatmap_max.map(h => ({ x: h.x_bin, y: h.y_bin, r: q_max != 0 ? h.count / q_max * max_radius : min_radius })), // this.calculateRadius(h.count, max_min, max_max, min_radius, max_radius) })),
            backgroundColor: 'rgba(0, 194, 0, 0.3)',
        };

        const min_max = Math.max(...chartData.heatmap_min.map(h => h.count));
        const min_min = Math.min(...chartData.heatmap_min.map(h => h.count));
        const q_min = chartData.heatmap_min.reduce((sum, c) => { return sum + c.count; }, 0);
        const heatmapMinDataset = {
            label: 'Minimums',
            type: 'bubble',
            xAxisID: 'xMain',
            yAxisID: 'yMain',
            data: chartData.heatmap_min.map(h => ({ x: h.x_bin, y: h.y_bin, r: q_min != 0 ? h.count / q_min * max_radius : min_radius })), // this.calculateRadius(h.count, min_min, min_max, min_radius, max_radius) })),
            backgroundColor: 'rgba(225, 0, 0, 0.3)',
        };

        // --- Line datasets ---
        const lineDatasets = chartData.line.datasets.map(d => ({
            ...d,
            type: 'line',
            xAxisID: 'xMain',
            yAxisID: 'yMain',
            borderColor: d.borderColor || 'blue',
            fill: false,
            borderWidth: 1,
            tension: 0.1,
            radius: 0,
            hidden: true,
        }));

        // --- Time histogram ---
        const timeHistMaxDataset = {
            label: 'Time Max Hist',
            type: 'bar',
            xAxisID: 'xMain',
            yAxisID: 'yTimeHist', // yTimeHist
            data: chartData.hist_time_max.data.map((v, i) => ({ x: chartData.hist_time_max.labels[i], y: v})),
            backgroundColor: 'rgba(0,150,0,0.8)',
        };
        const timeHistMinDataset = {
            label: 'Time Min Hist',
            type: 'bar',
            xAxisID: 'xMain',
            yAxisID: 'yTimeHist', // yTimeHist
            data: chartData.hist_time_min.data.map((v, i) => ({ x: chartData.hist_time_min.labels[i], y: v })),
            backgroundColor: 'rgba(225, 0, 0, 0.8)',
        };

        // --- Histogram lateral (precio) ---
        const priceHistMaxDataset = {
            label: 'Price Max Hist',
            type: 'bar',
            indexAxis: 'y',
            xAxisID: 'xPriceHist', // xPriceHist
            yAxisID: 'yMain',
            data: chartData.hist_price_max.data.map((v, i) => ({x: v, y: chartData.hist_price_max.labels[i]})),
            backgroundColor: 'rgba(0,150,0,0.8)',
        };
        const priceHistMinDataset = {
            label: 'Price Min Hist',
            type: 'bar',
            indexAxis: 'y',
            xAxisID: 'xPriceHist', // xPriceHist
            yAxisID: 'yMain',
            data: chartData.hist_price_min.data.map((v, i) => ({ x: v, y: chartData.hist_price_min.labels[i] })),
            backgroundColor: 'rgba(225, 0, 0, 0.8)',
        };

        // --- Configuración de Chart.js ---
        this.charts.executionOptimization = new Chart(ctxExecution.getContext("2d"), {
            type: 'line',
            data: {
                labels: chartData.line.labels,
                datasets: [
                    heatmapMaxDataset,
                    heatmapMinDataset,
                    ...lineDatasets,
                    timeHistMaxDataset,
                    timeHistMinDataset,
                    priceHistMaxDataset,
                    priceHistMinDataset
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    // Escalas principales para series y heatmap
                    xMain: {
                        type: 'linear',
                        position: 'bottom',
                        //stack: 'x',
                        //stackWeight: 2,
                        title: { display: true, text: 'Time' },
                    },
                    yMain: {
                        type: 'linear',
                        position: 'left',
                        //stack: 'y',
                        //stackWeight: 2,
                        title: { display: true, text: 'Price' },
                        // reverse: false,
                    },

                    // Eje para histograma lateral (precio)
                    xPriceHist: {
                        type: 'linear',
                        position: 'top', //'bottom',
                        //stack: 'x',
                        //offset: true,
                        //stackWeight: 1,
                        grid: { drawOnChartArea: false, drawTicks: false },
                        ticks: { display: true },
                    },

                    // Eje para histograma superior (tiempo)
                    yTimeHist: {
                        type: 'linear',
                        position: 'right', //'left',
                        //stack: 'y',
                        //offset: true,
                        //stackWeight: 1,
                        grid: { drawOnChartArea: false, drawTicks: false },
                        ticks: { display: true },
                    },
                    
                },
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            filter: function (legendItem, chartData) {
                                return legendItem.datasetIndex < chartData.datasets.length - 4;
                            }
                        }
                    },
                    zoom: {
                        mode: 'xy',
                        zoom: {
                            mode: 'xy',
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true,
                            },
                            drag: {
                                enabled: true,
                            },
                            onZoomComplete({chart}) {
                                // This update is needed to display up to date zoom level in the title.
                                // Without this, previous zoom level is displayed.
                                // The reason is: title uses the same beforeUpdate hook, and is evaluated before zoom.
                                chart.update('none');
                            }
                        },
                        // pan: {
                        //     mode: 'xy',
                        //     enabled: true,
                        // },
                    }
                },
                interaction: { mode: 'nearest', intersect: false },
            },
        });
    }
    
    async renderExecutionOptimizationOld() {
        const chartData = this.data.execution_optimization;
        if (!chartData) return;

        if (this.charts.executionOptimization) {
            this.charts.executionOptimization.destroy();
        }

        const ctxExecution = document.getElementById("executionOptimizationChart");
        if (!ctxExecution) return;

        // --- Heatmap datasets ---
        const max_radius = 15;
        const max_max = Math.max(...chartData.heatmap_max.map(h => h.count));
        const max_min = Math.min(...chartData.heatmap_max.map(h => h.count));
        const heatmapMaxDataset = {
            label: 'Maximums',
            type: 'bubble',
            xAxisID: 'xMain',
            yAxisID: 'yMain',
            data: chartData.heatmap_max.map(h => ({x: h.x_bin, y: h.y_bin, r: max_radius * (h.count - max_min)/(max_max - max_min)})),
            backgroundColor: 'rgba(0, 194, 0, 0.3)',
        };

        const min_max = Math.max(...chartData.heatmap_min.map(h => h.count));
        const min_min = Math.min(...chartData.heatmap_min.map(h => h.count));
        const heatmapMinDataset = {
            label: 'Minimums',
            type: 'bubble',
            xAxisID: 'xMain',
            yAxisID: 'yMain',
            data: chartData.heatmap_min.map(h => ({x: h.x_bin, y: h.y_bin, r: max_radius * (h.count - min_min)/(min_max - min_min)})),
            backgroundColor: 'rgba(225, 0, 0, 0.3)',
        };

        // --- Line datasets ---
        const lineDatasets = chartData.line.datasets.map(d => ({
            ...d,
            type: 'line',
            xAxisID: 'xMain',
            yAxisID: 'yMain',
            borderColor: d.borderColor || 'blue',
            fill: false,
            borderWidth: 1,
            tension: 0.1,
            radius: 0,
            hidden: true,
        }));

        // --- Histogram superior (tiempo) ---
        const timeHistDataset = {
            label: 'Distribución temporal',
            type: 'bar',
            xAxisID: 'xMain',
            yAxisID: 'yTimeHist',
            data: chartData.hist_time.data.map((v, i) => ({x: v, y: chartData.hist_time.labels[i]})),
            backgroundColor: 'rgba(0,150,0,0.8)',
        };

        // --- Histogram lateral (precio) ---
        const priceHistDataset = {
            label: 'Distribución de precios',
            type: 'bar',
            indexAxis: 'y',
            xAxisID: 'xPriceHist',
            yAxisID: 'yMain',
            data: chartData.hist_price.data.map((v, i) => ({x: v, y: chartData.hist_price.labels[i]})),
            backgroundColor: 'rgba(0,150,0,0.8)',
        };

        // --- Configuración de Chart.js ---
        this.charts.executionOptimization = new Chart(ctxExecution.getContext("2d"), {
            type: 'line',
            data: {
                labels: chartData.line.labels,
                datasets: [
                    heatmapMaxDataset,
                    heatmapMinDataset,
                    ...lineDatasets,
                    timeHistDataset,
                    priceHistDataset
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    // Escalas principales para series y heatmap
                    xMain: {
                        type: 'category',
                        position: 'bottom',
                        stack: 'x',
                        stackWeight: 2,
                        title: { display: true, text: 'Tiempo' },
                    },
                    yMain: {
                        type: 'linear',
                        position: 'left',
                        stack: 'y',
                        stackWeight: 2,
                        title: { display: true, text: 'Precio' },
                        reverse: false,
                    },

                    // Eje para histograma lateral (precio)
                    xPriceHist: {
                        type: 'linear',
                        position: 'bottom',
                        stack: 'x',
                        offset: true,
                        stackWeight: 1,
                        grid: { drawOnChartArea: false, drawTicks: false },
                        ticks: { display: false },
                    },

                    // Eje para histograma superior (tiempo)
                    yTimeHist: {
                        type: 'linear',
                        position: 'left',
                        stack: 'y',
                        offset: true,
                        stackWeight: 1,
                        grid: { drawOnChartArea: false, drawTicks: false },
                        ticks: { display: false },
                    },
                },
                plugins: {
                    legend: { display: true },
                    zoom: {
                        mode: 'xy',
                        zoom: {
                            mode: 'xy',
                            wheel: {
                                enabled: true,
                            },
                            pinch: {
                                enabled: true,
                            },
                            drag: {
                                enabled: true,
                            },
                            onZoomComplete({chart}) {
                                // This update is needed to display up to date zoom level in the title.
                                // Without this, previous zoom level is displayed.
                                // The reason is: title uses the same beforeUpdate hook, and is evaluated before zoom.
                                console.log('Zoom finished');
                                chart.update('none');
                            }
                        },
                        pan: {
                            mode: 'xy',
                            enabled: true,
                        },
                    }
                },
                interaction: { mode: 'nearest', intersect: false },
            },
        });
    }


    async renderCharts() {
        this.renderEquityChart();
        this.renderPnlDistribution();
        this.renderDailyReturn();
        this.renderMonthlyReturn();
        this.renderWeekdayExpectancy();
        this.renderHourlyExpectancy();
        this.renderSymbolPortion();
        this.renderHoldTime();
        this.renderExecutionOptimization();
    }
}

class Stats {
    constructor(data, show_r=false) {
        this.data = data;
        this.show_r = show_r;
    }

    async renderStats () {
        return;
    }

    renderAll (data = null, show_r=null) {
        if (data) {
            this.data = data;
        }
        if (show_r) {
            this.show_r = show_r;
        }
        console.log('Rendering stats:', data);
        this.renderStats()
    }

    async applyColorClasses () {
        // Apply positive/negative classes to values
        const elements = document.querySelectorAll('.stat-value');
        elements.forEach(el => {
            const text = el.textContent;
            if (text.includes('-') && !text.includes('ratio') && !text.includes('Ratio')) {
                if (!el.classList.contains('text-loss')) {
                    el.classList.add('text-loss');
                }
            } else if (text.includes('%') || text.includes('$')) {
                const numValue = parseFloat(text.replace(/[^0-9.-]/g, ''));
                if (numValue > 0) {
                    if (!el.classList.contains('text-profit')) {
                        el.classList.add('text-profit');
                    }
                } else if (numValue < 0) {
                    if (!el.classList.contains('text-loss')) {
                        el.classList.add('text-loss');
                    }
                }
            }
        });
    }
}

class TradeStats extends Stats {
    constructor(data, show_r=false) {
        super(data, show_r);
    }

    async renderStats () {
        document.getElementById('total-pnl').innerHTML = `${formatNumber(this.data.total_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('total-pnl').className = 'summary-value ' + (this.data.total_pnl > 0 ? 'text-profit' : 'text-loss');
        document.getElementById('win-rate').innerHTML = `${formatNumber(this.data.win_rate, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('total-trades').textContent = this.data.total_trades;
        document.getElementById('risk-reward').innerHTML = `${this.data.risk_reward.toFixed(2)}`;
        document.getElementById('risk-reward').className = 'summary-value ' + (this.data.risk_reward > 1 ? 'text-profit' : 'text-loss');

        
        document.getElementById('total-pnl-stat').innerHTML = `${formatNumber(this.data.total_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('win-rate-stat').innerHTML = `${formatNumber(this.data.win_rate, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('total-trades-stat').textContent = this.data.total_trades;

        document.getElementById('winning-trades').innerHTML = `${this.data.winning_trades}`;
        document.getElementById('losing-trades').innerHTML = `${this.data.losing_trades}`;
        document.getElementById('scratch-trades').innerHTML = `${this.data.scratch_trades}`;

        document.getElementById('avg-trade').innerHTML = `${formatNumber(this.data.avg_trade_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-share').innerHTML = `${formatNumber(this.data.avg_pnl_per_share, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('median').innerHTML = `${formatNumber(this.data.median_trade_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('largest-gain').innerHTML = `${formatNumber(this.data.largest_gain, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('largest-loss').innerHTML = `${formatNumber(this.data.largest_loss, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;

        document.getElementById('winning-pnl').innerHTML = `${formatNumber(this.data.winning_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('losing-pnl').innerHTML = `${formatNumber(this.data.losing_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-win').innerHTML = `${formatNumber(this.data.avg_win, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-loss').innerHTML = `${formatNumber(this.data.avg_loss, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;

        document.getElementById('risk-reward-stat').innerHTML = `${this.data.risk_reward.toFixed(2)}`;
        document.getElementById('profit-factor').innerHTML = `${this.data.profit_factor.toFixed(2)}`;
        document.getElementById('sharpe').innerHTML = `${this.data.sharpe_ratio.toFixed(2)}`;
        document.getElementById('drawdown').innerHTML = `${formatNumber(this.data.max_drawdown, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('std').innerHTML = `${formatNumber(this.data.trade_pnl_std, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('sqn').innerHTML = `${this.data.sqn.toFixed(2)}`;

        document.getElementById('k-ratio').innerHTML = `${this.data.k_ratio.toFixed(2)}`;
        document.getElementById('kelly').innerHTML = `${formatNumber(this.data.kelly_percent, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('p-value').innerHTML = `${this.data.p_value.toFixed(4)}`;
        document.getElementById('avg-daily').innerHTML = `${formatNumber(this.data.avg_daily_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-volume').innerHTML = `${formatNumber(this.data.avg_daily_volume, 'currency', 1, 2, 'compact')}`;

        document.getElementById('max-wins').innerHTML = `${this.data.max_consecutive_wins}`;
        document.getElementById('max-losses').innerHTML = `${this.data.max_consecutive_losses}`;

        // General Stats Tab
        document.getElementById('total-commissions').textContent = formatNumber(this.data.total_commissions, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');
        document.getElementById('total-fees').textContent = formatNumber(this.data.total_fees, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');
        document.getElementById('total-costs').textContent = formatNumber(this.data.total_commissions + this.data.total_fees, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');
        document.getElementById('cost-per-trade').textContent = formatNumber((this.data.total_commissions + this.data.total_fees) / this.data.total_trades, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');

        const costImpact = ((this.data.gross?.total_pnl - this.data.net?.total_pnl) / this.data.gross?.total_pnl) * 100;
        document.getElementById('cost-impact').textContent = formatNumber(costImpact, 'percentage', 1, 2, 'compact');

        document.getElementById('hold-overall').textContent = this.data.avg_hold_time_overall;
        document.getElementById('hold-winners').textContent = this.data.avg_hold_time_winners;
        document.getElementById('hold-losers').textContent = this.data.avg_hold_time_losers;
        document.getElementById('hold-scratches').textContent = this.data.avg_hold_time_scratches;

        document.getElementById('avg-mfe').textContent = formatNumber(this.data.avg_mfe, 'currency', 1, 2, 'compact');
        document.getElementById('avg-mae').textContent = formatNumber(this.data.avg_mae, 'currency', 1, 2, 'compact');

        const mfeMaeRatio = Math.abs(this.data.avg_mfe / this.data.avg_mae);
        document.getElementById('mfe-mae-ratio').textContent = mfeMaeRatio.toFixed(2);

        document.getElementById('max-wins').innerHTML = `${this.data.max_consecutive_wins}`;
        document.getElementById('max-losses').innerHTML = `${this.data.max_consecutive_losses}`;

        // Apply color classes based on values
        this.applyColorClasses();
    }
}

class WatchlistStats extends Stats {
    constructor(data, show_r=false) {
        super(data, show_r);
    }

    async renderSectorAnalysis(sector_data) {
        const tbody = document.getElementById('sectorTableBody');
        
        tbody.innerHTML = '';
        
        // Sort sectors by average return
        const sorted_sectors = Object.entries(sector_data)
            .sort(([,a], [,b]) => b.avg_return - a.avg_return);
        
        sorted_sectors.forEach(([sector, data]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="sector-badge">${sector}</span></td>
                <td class="${data.avg_return >= 0 ? 'text-profit' : 'text-loss'}">${data.avg_return}%</td>
                <td>${data.count}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async renderStats () {
        document.getElementById('total-pnl').innerHTML = `${formatNumber(this.data.total_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('total-pnl').className = 'summary-value ' + (this.data.total_pnl > 0 ? 'text-profit' : 'text-loss');
        document.getElementById('win-rate').innerHTML = `${formatNumber(this.data.win_rate, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('total-trades').textContent = this.data.total_trades;
        document.getElementById('risk-reward').innerHTML = `${this.data.risk_reward.toFixed(2)}`;
        document.getElementById('risk-reward').className = 'summary-value ' + (this.data.risk_reward > 1 ? 'text-profit' : 'text-loss');


        document.getElementById('total-pnl-stat').innerHTML = `${formatNumber(this.data.total_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('win-rate-stat').innerHTML = `${formatNumber(this.data.win_rate, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('total-trades-stat').textContent = this.data.total_trades;

        document.getElementById('winning-trades').innerHTML = `${this.data.winning_trades}`;
        document.getElementById('losing-trades').innerHTML = `${this.data.losing_trades}`;
        document.getElementById('scratch-trades').innerHTML = `${this.data.scratch_trades}`;

        document.getElementById('avg-trade').innerHTML = `${formatNumber(this.data.avg_trade_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-share').innerHTML = `${formatNumber(this.data.avg_pnl_per_share, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('median').innerHTML = `${formatNumber(this.data.median_trade_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('largest-gain').innerHTML = `${formatNumber(this.data.largest_gain, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('largest-loss').innerHTML = `${formatNumber(this.data.largest_loss, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;

        document.getElementById('winning-pnl').innerHTML = `${formatNumber(this.data.winning_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('losing-pnl').innerHTML = `${formatNumber(this.data.losing_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-win').innerHTML = `${formatNumber(this.data.avg_win, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-loss').innerHTML = `${formatNumber(this.data.avg_loss, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;

        document.getElementById('risk-reward-stat').innerHTML = `${this.data.risk_reward.toFixed(2)}`;
        document.getElementById('profit-factor').innerHTML = `${this.data.profit_factor.toFixed(2)}`;
        document.getElementById('sharpe').innerHTML = `${this.data.sharpe_ratio.toFixed(2)}`;
        document.getElementById('drawdown').innerHTML = `${formatNumber(this.data.max_drawdown, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('std').innerHTML = `${formatNumber(this.data.trade_pnl_std, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('sqn').innerHTML = `${this.data.sqn.toFixed(2)}`;

        document.getElementById('k-ratio').innerHTML = `${this.data.k_ratio.toFixed(2)}`;
        document.getElementById('kelly').innerHTML = `${formatNumber(this.data.kelly_percent, 'percentage', 1, 2, 'compact')}`;
        document.getElementById('p-value').innerHTML = `${this.data.p_value.toFixed(4)}`;
        document.getElementById('avg-daily').innerHTML = `${formatNumber(this.data.avg_daily_pnl, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact')}`;
        document.getElementById('avg-volume').innerHTML = `${formatNumber(this.data.avg_daily_volume, 'currency', 1, 2, 'compact')}`;

        document.getElementById('max-wins').innerHTML = `${this.data.max_consecutive_wins}`;
        document.getElementById('max-losses').innerHTML = `${this.data.max_consecutive_losses}`;

        // General Stats Tab
        document.getElementById('total-commissions').textContent = formatNumber(this.data.total_commissions, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');
        document.getElementById('total-fees').textContent = formatNumber(this.data.total_fees, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');
        document.getElementById('total-costs').textContent = formatNumber(this.data.total_commissions + this.data.total_fees, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');
        document.getElementById('cost-per-trade').textContent = formatNumber((this.data.total_commissions + this.data.total_fees) / this.data.total_trades, this.show_r ? 'r_multiple' : 'currency', 1, 2, 'compact');

        const costImpact = ((this.data.gross?.total_pnl - this.data.net?.total_pnl) / this.data.gross?.total_pnl) * 100;
        document.getElementById('cost-impact').textContent = formatNumber(costImpact, 'percentage', 1, 2, 'compact');

        document.getElementById('hold-overall').textContent = this.data.avg_hold_time_overall;
        document.getElementById('hold-winners').textContent = this.data.avg_hold_time_winners;
        document.getElementById('hold-losers').textContent = this.data.avg_hold_time_losers;
        document.getElementById('hold-scratches').textContent = this.data.avg_hold_time_scratches;

        document.getElementById('avg-mfe').textContent = formatNumber(this.data.avg_mfe, 'currency', 1, 2, 'compact');
        document.getElementById('avg-mae').textContent = formatNumber(this.data.avg_mae, 'currency', 1, 2, 'compact');

        const mfeMaeRatio = Math.abs(this.data.avg_mfe / this.data.avg_mae);
        document.getElementById('mfe-mae-ratio').textContent = mfeMaeRatio.toFixed(2);

        document.getElementById('max-wins').innerHTML = `${this.data.max_consecutive_wins}`;
        document.getElementById('max-losses').innerHTML = `${this.data.max_consecutive_losses}`;

        this.renderSectorAnalysis(this.data.sectors_stats);


        // Apply color classes based on values
        this.applyColorClasses();
    }
}

class Performance {
    constructor(stats_data, charts_data, gross=false, show_r=false, endpoint=null, chartsCommonOptions=null, StatsObject=Stats, ChartsObject=Charts) {
        this.stats_data = stats_data;
        this.charts_data = charts_data;
        this.gross = gross;
        this.show_r = show_r;
        this.endpoint = endpoint;
        this.statsObject = new StatsObject(this.gross ? this.stats_data.gross : this.stats_data.net, show_r);
        this.chartsObject = new ChartsObject(this.gross ? this.charts_data.gross : this.charts_data.net, chartsCommonOptions, show_r);

        this.init();
    }
    
    async init() {
        try {
            this.showLoading(true);
            if (this.stats_data === null) await this.loadStatsData();
            if (this.charts_data === null) await this.loadChartsData();
            this.renderAll();
            this.showLoading(false);
        } catch (error) {
            this.showError(error.message, true);
        }
    }
    
    async loadStatsData() {
        const response = await fetch(this.endpoint || `/api/journal/performance/stats`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error when loading data');
        }
        
        this.stats_data = await response.json();
    }
    
    async loadChartsData() {
        const response = await fetch(this.endpoint || `/api/journal/performance/charts`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error when loading data');
        }
        
        this.charts_data = await response.json();
    }
    
    showLoading(show=true) {
        if (show) {
            document.getElementById('errorState').classList.add('d-none');
            document.getElementById('errorMessage').textContent = '';
            document.getElementById('mainContent').classList.add('d-none');
            document.getElementById('loadingState').classList.remove('d-none');
        } else {
            document.getElementById('loadingState').classList.add('d-none');
            document.getElementById('mainContent').classList.remove('d-none');
        }
    }
    
    showError(message, show=true) {
        if (show) {
            document.getElementById('loadingState').classList.add('d-none');
            document.getElementById('mainContent').classList.add('d-none');
            document.getElementById('errorState').classList.remove('d-none');
            document.getElementById('errorMessage').textContent = message;
        } else {
            document.getElementById('errorState').classList.add('d-none');
            document.getElementById('errorMessage').textContent = '';
        }
    }
    
    renderAll() {
        this.renderStats();
        this.renderCharts();
    }
    
    async renderStats () {
        this.statsObject.renderAll(this.gross ? this.stats_data.gross : this.stats_data.net, this.show_r);
    }

    async renderCharts () {
        this.chartsObject.renderAll(this.gross ? this.charts_data.gross : this.charts_data.net, this.show_r);
    }

    async changeGrossNet(gross=false) {
        console.log('Gross/Net toggle changed. Is now gross?', this.gross, 'Should be?', gross);
        this.showLoading(true);
        if (gross) {
            console.log('Making it gross');
            this.gross = true;
            this.renderAll();
        } else {
            console.log('Making it net');
            this.gross = false;
            this.renderAll();
        }
        console.log('Is now gross?', this.gross);
        this.showLoading(false);
    }
}

