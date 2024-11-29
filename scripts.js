document.getElementById('generate-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const service = document.getElementById('service').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service, username, password }),
    });
    const result = await response.json();
    alert(result.message || result.error);
});

document.getElementById('retrieve-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const service = document.getElementById('retrieve-service').value;
    const username = document.getElementById('retrieve-username').value;

    const response = await fetch('/retrieve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service, username }),
    });
    const result = await response.json();
    document.getElementById('result').textContent = result.password || result.error;
});
