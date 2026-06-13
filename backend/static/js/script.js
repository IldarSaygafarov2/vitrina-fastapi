// TODO: узнать у пользователя его username из телеграмма - если есть написать приветствие в зависимости от роли


const API_URL = 'http://127.0.0.1:8888/api/v1';

async function login(username) {
    const response = await fetch(`${API_URL}/users/login/`, {
        method: 'POST',
        credentials: 'include', // важно! передаёт и сохраняет cookie
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "tg_username": username })
    });

    return await response.json();
}


async function checkAuth() {
    const response = await fetch(`${API_URL}/users/me`, {
        credentials: 'include'
    });

    if (response.ok) {
        const user = await response.json();
        return user; // пользователь авторизован
    }

    return null; // не авторизован
}

async function logout() {
    await fetch(`${API_URL}/users/logout`, {
        method: 'POST',
        credentials: 'include'
    });
}

async function makeRequest(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`);
    const result = await response.json();
    return result;
}



document.addEventListener('DOMContentLoaded', async () => {
    const logoutBtn = document.querySelector('#logout-btn');

    const isAuthenticated = await checkAuth();
    console.log(isAuthenticated)

    if (!isAuthenticated) {
        let username = prompt('telegram username: ')
        let user = await login(username);
        console.log(user)
        logoutBtn.classList.add('hidden')
    } else {
        console.log('authenticated')
        logoutBtn.addEventListener('click', logout)
        logoutBtn.classList.remove('hidden')
    }
})