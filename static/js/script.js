document.addEventListener('DOMContentLoaded', () => {
    const ctx1 = document.getElementById('occupancy-rate').getContext('2d');
    const ctx2 = document.getElementById('monthly-room-revenue').getContext('2d');
    const ctx3 = document.getElementById('breakfast-orders').getContext('2d');
    const ctx4 = document.getElementById('monthly-breakfast-revenue').getContext('2d');
    const ctx5 = document.getElementById('planning').getContext('2d');
    const ctx6 = document.getElementById('global-monthly-revenue').getContext('2d');

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
    };

    new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: ['Booked', 'Flopped'],
            datasets: [{
                data: [36.2, 63.8],
                backgroundColor: ['#6a5acd', '#ddd']
            }]
        },
        options: chartOptions
    });

    new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Revenue per month room',
                data: [10, 15, 20, 25, 30, 15, 20, 25, 20, 30, 25, 30],
                backgroundColor: '#6a5acd'
            }]
        },
        options: {
            layout: {
                padding: 8
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });

    new Chart(ctx3, {
        type: 'pie',
        data: {
            labels: ['Croissant', 'Pain au chocolat', 'Pain 1/2 par Voya'],
            datasets: [{
                data: [7, 5, 12],
                backgroundColor: ['#6a5acd', '#ddd', '#bbb']
            }]
        },
        options: {layout: {
            padding: 8
        },
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              }
            },
            maintainAspectRatio: false,
          },
        });

    new Chart(ctx4, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Avr', 'Mai', 'Jui', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Revenue par mois Petit-Déj',
                data: [10000, 15000, 20000, 25000, 30000, 35000, 30000, 25000, 20000, 15000, 10000, 5000],
                backgroundColor: '#6a5acd'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: 16
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });

    new Chart(ctx5, {
        type: 'bar',
        data: {
            labels: ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'],
            datasets: [{
                label: 'Planning',
                data: [5, 6, 4, 3, 2, 1],
                backgroundColor: '#6a5acd'
            }]
        },
        options: {
            layout: {
                padding: 8
            },
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });
    

    new Chart(ctx6, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Avr', 'Mai', 'Jui', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Revenue par mois global',
                data: [15000, 20000, 25000, 30000, 35000, 40000, 45000, 40000, 35000, 30000, 25000, 20000],
                backgroundColor: '#6a5acd'
            }]
        },
        options: {
            
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true
                }
            }
        }
    });
});
