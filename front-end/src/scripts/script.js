fetch('http://localhost:8000/training_progress')
    .then(response => response.json())
    .then(data => {
        console.log('API Response:', data);
        if (!data.epoch_losses) {
            console.error('No epoch_losses found in response');
            return;
        }
        const ctx = document.getElementById('lossChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({ length: data.epoch_losses.length }, (_, i) => i + 1),
                datasets: [{
                    label: 'Epoch Loss',
                    data: data.epoch_losses,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: 'Epoch' } },
                    y: { title: { display: true, text: 'Loss' } }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching training progress:', error));