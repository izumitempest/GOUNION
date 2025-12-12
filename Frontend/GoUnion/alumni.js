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
            alert("Friend request sent!");
        } else {
            const data = await res.json();
            alert(data.detail || "Failed to send request");
        }
    } catch (err) {
        alert("Error: " + err.message);
    }
}

// Load all users on page load
loadAllUsers();
