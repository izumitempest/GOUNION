const API_URL = "http://127.0.0.1:8001";
const token = localStorage.getItem("access_token");

 if (!token) {
    window.location.href = "login.html";
}

const searchInput = document.getElementById("searchInput");
const resultsContainer = document.getElementById("resultsContainer");
const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");

// Sidebar toggle
toggleBtn.addEventListener("click", () => {
    sidebar.style.left = sidebar.style.left === "0px" ? "-260px" : "0px";
});

// Search with debounce
let searchTimeout;
searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            searchUsers(query);
        } else {
            loadAllUsers();
        }
    }, 300);
});

async function loadAllUsers() {
    try {
        const res = await fetch(`${API_URL}/search/users?q=`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const users = await res.json();
        renderUsers(users);
    } catch (err) {
        console.error("Failed to load users:", err);
    }
}

async function searchUsers(query) {
    try {
        const res = await fetch(`${API_URL}/search/users?q=${encodeURIComponent(query)}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const users = await res.json();
        renderUsers(users);
    } catch (err) {
        console.error("Search failed:", err);
        resultsContainer.innerHTML = "<p>Search failed. Please try again.</p>";
    }
}

function renderUsers(users) {
    resultsContainer.innerHTML = "";

    if (users.length === 0) {
        resultsContainer.innerHTML = "<p style='text-align: center; color: #888;'>No users found.</p>";
        return;
    }

    users.forEach(user => {
        const card = document.createElement("div");
        card.className = "user-card";
        card.style.cssText = "background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; display: flex; align-items: center; gap: 15px;";

        const avatar = document.createElement("div");
        avatar.style.cssText = "width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: bold;";
        avatar.textContent = user.username.charAt(0).toUpperCase();

        const info = document.createElement("div");
        info.style.flex = "1";
        info.innerHTML = `
            <h3 style="margin: 0 0 5px 0; font-size: 18px;">@${user.username}</h3>
            <p style="margin: 0; color: #666; font-size: 14px;">${user.email}</p>
        `;

        const actionBtn = document.createElement("button");
        actionBtn.textContent = "Connect";
        actionBtn.style.cssText = "padding: 8px 20px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;";
        actionBtn.onclick = () => sendFriendRequest(user.id);

        card.appendChild(avatar);
        card.appendChild(info);
        card.appendChild(actionBtn);
        resultsContainer.appendChild(card);
    });
}

async function sendFriendRequest(userId) {
    try {
        const res = await fetch(`${API_URL}/friend-request/${userId}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (res.ok) {
            showNotification("Friend request sent!", "success");
            // Change button state
            const btn = document.querySelector(`button[onclick="sendFriendRequest('${userId}')"]`);
            if (btn) {
                btn.textContent = "Request Sent";
                btn.style.background = "#28a745";
                btn.disabled = true;
            }
        } else {
            const data = await res.json();
            showNotification(data.detail || "Failed to send request", "error");
        }
    } catch (err) {
        showNotification("Error: " + err.message, "error");
    }
}

// Notification function (Reusing standard toast)
function showNotification(message, type="info") {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = message;
    
    const bgColor = type === 'success' ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)' :
                    type === 'error' ? 'linear-gradient(135deg, #ef4444 0%, #fca5a5 100%)' :
                    'linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%)';
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease, fadeOut 0.3s ease 2.7s;
        animation-fill-mode: forwards;
        max-width: 300px;
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove
    setTimeout(() => {
        if (notification.parentNode) notification.remove();
    }, 3000);
}

// Load all users on page load
loadAllUsers();
