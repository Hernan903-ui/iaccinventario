document.addEventListener('DOMContentLoaded', () => {
    fetch('/analytics_data')
        .then(response => response.json())
        .then(data => {
            createChart('mostSoldChart', data.most_sold, 'Productos Más Vendidos');
            createChart('lowDemandChart', data.low_demand, 'Productos de Baja Demanda');
            createStockChart('lowStockChart', data.low_stock, 'Productos con Bajo Stock');
        })
        .catch(error => console.error('Error:', error));

    function createChart(chartId, chartData, chartTitle) {
        const ctx = document.getElementById(chartId).getContext('2d');
        const labels = chartData.map(item => item.name);
        const data = chartData.map(item => item.quantity);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: chartTitle,
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cantidad'
                        }
                    },
                     x: {
                        title: {
                            display: true,
                            text: 'Producto'
                        }
                    }
                }
            }
        });
    }
     function createStockChart(chartId, chartData, chartTitle) {
        const ctx = document.getElementById(chartId).getContext('2d');
        const labels = chartData.map(item => item.name);
        const data = chartData.map(item => item.stock);

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: chartTitle,
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                 responsive: true,
                plugins: {
                   legend: {
                        position: 'top',
                    },
                     title: {
                        display: true,
                        text: 'Productos'
                    }
                }
            }
        });
    }
});