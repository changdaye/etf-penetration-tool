let currentEtfList = [];
let currentSummary = [];
let industryChart = null;
let top10BarChart = null;
let showAmount = false;

document.addEventListener('DOMContentLoaded', function() {
    initUpload();
    initButtons();
});

function initUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');
    
    uploadBox.addEventListener('click', function() { fileInput.click(); });
    
    uploadBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });
    
    uploadBox.addEventListener('dragleave', function() {
        uploadBox.classList.remove('dragover');
    });
    
    uploadBox.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) handleFile(file);
    });
    
    const toggle = document.getElementById('showAmountToggle');
    if (toggle) {
        toggle.addEventListener('change', function(e) {
            showAmount = e.target.checked;
            refreshDisplay();
        });
    }
}

function initButtons() {
    document.getElementById('analyzeBtn').addEventListener('click', analyze);
    document.getElementById('exportBtn').addEventListener('click', exportResults);
}

async function handleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (data.success) {
            currentEtfList = data.etf_list;
            showEtfList(data);
        } else {
            alert('错误：' + data.error);
        }
    } catch (error) {
        alert('上传失败：' + error.message);
    }
}

function showEtfList(data) {
    document.getElementById('etfCount').textContent = data.etf_count;
    document.getElementById('totalAmount').textContent = formatNumber(data.total_amount);
    
    const tbody = document.querySelector('#etfTable tbody');
    tbody.innerHTML = '';
    
    data.etf_list.forEach(function(etf) {
        const pct = data.total_amount > 0 ? (etf.amount / data.total_amount * 100).toFixed(1) : 0;
        const row = '<tr><td>' + etf.code + '</td><td>' + (etf.name || '-') + '</td><td>' + formatNumber(etf.amount) + '</td><td>' + pct + '%</td></tr>';
        tbody.innerHTML += row;
    });
    
    document.getElementById('etfListSection').style.display = 'block';
}

async function analyze() {
    document.getElementById('etfListSection').style.display = 'none';
    document.getElementById('progressSection').style.display = 'block';
    
    const totalAmount = currentEtfList.reduce(function(sum, etf) { return sum + etf.amount; }, 0);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ etf_list: currentEtfList, total_amount: totalAmount })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSummary = data.summary;
            showResults(data);
        } else {
            alert('分析失败：' + data.error);
            location.reload();
        }
    } catch (error) {
        alert('分析失败：' + error.message);
        location.reload();
    }
}

function refreshDisplay() {
    if (currentSummary.length > 0) {
        const total = currentSummary.reduce(function(sum, item) { return sum + item['穿透金额']; }, 0);
        const penetrationElement = document.getElementById('penetrationAmount');
        if (penetrationElement) {
            penetrationElement.textContent = showAmount ? ('¥' + formatNumber(total)) : '******';
        }
        renderResultTable(currentSummary);
        
        if (industryChart) {
            industryChart.destroy();
            industryChart = null;
        }
        if (top10BarChart) {
            top10BarChart.destroy();
            top10BarChart = null;
        }
        
        const resultSection = document.getElementById('resultSection');
        if (resultSection && resultSection.style.display !== 'none') {
            const industryDist = currentSummary.reduce(function(acc, item) {
                const ind = item['所属行业'];
                if (!acc[ind]) acc[ind] = 0;
                acc[ind] += item['穿透金额'];
                return acc;
            }, {});
            
            const industryData = Object.keys(industryDist).map(function(key) {
                return { '所属行业': key, '穿透金额': industryDist[key] };
            }).sort(function(a, b) { return b['穿透金额'] - a['穿透金额']; });
            
            renderIndustryChart(industryData);
            renderTop10BarChart();
        }
    }
}

function showResults(data) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'block';
    
    document.getElementById('stockCount').textContent = data.stock_count;
    
    const penetrationElement = document.getElementById('penetrationAmount');
    if (penetrationElement) {
        penetrationElement.textContent = showAmount ? ('¥' + formatNumber(data.penetration_amount)) : '******';
    }
    
    document.getElementById('coverage').textContent = data.coverage + '%';
    
    document.getElementById('top50Bar').style.width = data.concentration.top50 + '%';
    document.getElementById('top50Value').textContent = data.concentration.top50 + '%';
    document.getElementById('top100Bar').style.width = data.concentration.top100 + '%';
    document.getElementById('top100Value').textContent = data.concentration.top100 + '%';
    document.getElementById('top200Bar').style.width = data.concentration.top200 + '%';
    document.getElementById('top200Value').textContent = data.concentration.top200 + '%';
    document.getElementById('top500Bar').style.width = data.concentration.top500 + '%';
    document.getElementById('top500Value').textContent = data.concentration.top500 + '%';
    
    renderIndustryChart(data.industry_distribution);
    renderTop10BarChart();
    renderResultTable(data.summary);
}

function renderIndustryChart(industryData) {
    const ctx = document.getElementById('industryChart').getContext('2d');
    const top10 = industryData.slice(0, 10);
    const total = top10.reduce(function(sum, item) { return sum + item['穿透金额']; }, 0);
    
    if (industryChart) industryChart.destroy();
    
    industryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: top10.map(function(item) { return item['所属行业']; }),
            datasets: [{
                data: top10.map(function(item) { return item['穿透金额']; }),
                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.5,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 9 }, padding: 5 } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const pct = ((value / total) * 100).toFixed(1);
                            return showAmount ? (label + ': ¥' + value.toLocaleString() + ' (' + pct + '%)') : (label + ': ' + pct + '%');
                        }
                    }
                },
                datalabels: {
                    color: '#fff',
                    font: { size: 9, weight: 'bold' },
                    formatter: function(value, context) {
                        const label = context.chart.data.labels[context.dataIndex];
                        const pct = ((value / total) * 100).toFixed(1);
                        if (showAmount) {
                            const amt = value >= 10000 ? ((value/10000).toFixed(1) + '万') : Math.round(value);
                            return label + '\n¥' + amt + '\n' + pct + '%';
                        } else {
                            return label + '\n' + pct + '%';
                        }
                    },
                    anchor: 'center',
                    align: 'center'
                }
            }
        }
    });
}

function renderTop10BarChart() {
    const ctx = document.getElementById('industryBarChart').getContext('2d');
    const top10 = currentSummary.slice(0, 10);
    
    if (top10BarChart) top10BarChart.destroy();
    
    top10BarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(function(item) { return item['股票名称']; }),
            datasets: [{
                label: '穿透金额',
                data: top10.map(function(item) { return item['穿透金额']; }),
                backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.5,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw || 0;
                            const stock = context.label || '';
                            if (showAmount) {
                                return stock + ': ¥' + value.toLocaleString();
                            } else {
                                return stock;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (showAmount) {
                                return value >= 10000 ? '¥' + (value/10000).toFixed(1) + '万' : '¥' + value;
                            } else {
                                return '';
                            }
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: { size: 9 }
                    }
                }
            }
        }
    });
}

function renderResultTable(summary) {
    const tbody = document.querySelector('#resultTable tbody');
    tbody.innerHTML = '';
    
    summary.forEach(function(item, index) {
        const amountText = showAmount ? formatNumber(item['穿透金额']) : '******';
        const row = '<tr><td>' + (index + 1) + '</td><td>' + item['股票代码'] + '</td><td>' + item['股票名称'] + '</td><td>' + item['所属行业'] + '</td><td>' + item['占总持仓%'] + '%</td><td class="amount-cell">' + amountText + '</td><td>' + item['ETF 数量'] + '</td></tr>';
        tbody.innerHTML += row;
    });
}

async function exportResults() {
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ summary: currentSummary })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ETF 穿透分析_' + new Date().toISOString().slice(0,19).replace(/[:-]/g,'') + '.xlsx';
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert('导出失败：' + error.message);
    }
}

function formatNumber(num) {
    return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
}
