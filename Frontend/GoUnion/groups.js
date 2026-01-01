function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const navLinks = document.getElementById('navLinks');
    const menuToggle = document.querySelector('.menu-toggle');
    
    if (!navLinks.contains(event.target) && !menuToggle.contains(event.target)) {
        navLinks.classList.remove('active');
    }
});

// Add click listeners to join buttons
const API_URL = "http://127.0.0.1:8001";
const token = localStorage.getItem("access_token");

document.addEventListener('DOMContentLoaded', function() {
    loadGroups();
    setupSearch();
    setupCreateGroup();
    
    // Add CSS for fadeIn animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .loading-text {
            display: inline-block;
            animation: pulse 0.5s ease infinite;
        }
    `;
    document.head.appendChild(style);
});

async function loadGroups() {
    const grid = document.querySelector('.groups-grid');
    grid.innerHTML = '<div style="color: white; text-align: center; grid-column: 1/-1;">Loading groups...</div>';
    
    try {
        const res = await fetch(`${API_URL}/groups/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to load groups");
        
        const groups = await res.json();
        grid.innerHTML = '';
        
        if (groups.length === 0) {
            grid.innerHTML = '<div style="color: #b0b0c0; text-align: center; grid-column: 1/-1;">No groups found. Create one?</div>';
            return;
        }
        
        groups.forEach(group => {
            const card = createGroupCard(group);
            grid.appendChild(card);
        });
        
    } catch (err) {
        console.error("Error loading groups:", err);
        grid.innerHTML = '<div style="color: #ef4444; text-align: center; grid-column: 1/-1;">Failed to load groups.</div>';
    }
}

function createGroupCard(group) {
    const card = document.createElement('div');
    card.className = 'group-card';
    card.innerHTML = `
        <div class="group-icon">${group.name.charAt(0)}</div>
        <h3>${group.name}</h3>
        <p>${group.description || 'No description'}</p>
        <div class="group-stats">
            <span><i class="fas fa-users"></i> ${group.members_count || 0} Members</span>
            <span><i class="fas fa-circle"></i> Active</span>
        </div>
        <button onclick="joinGroup('${group.id}', this, '${group.name}')">Join</button>
    `;
    return card;
}

window.joinGroup = async function(groupId, btn, groupName) {
    const originalText = btn.textContent;
    btn.textContent = 'Joining...';
    btn.disabled = true;
    
    try {
        const res = await fetch(`${API_URL}/groups/${groupId}/join`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (res.ok) {
            btn.textContent = 'Joined ✓';
            btn.style.background = 'linear-gradient(135deg, #10b981 0%, #34d399 100%)';
            btn.style.boxShadow = '0 8px 20px rgba(16, 185, 129, 0.4)';
            showNotification(`Successfully joined "${groupName}"!`);
        } else {
            const data = await res.json();
             // specific handling if already joined
             if (res.status === 400 && data.detail.includes("already")) {
                 btn.textContent = 'Joined ✓';
                 btn.style.background = '#10b981';
                 showNotification(`You are already in "${groupName}"`);
             } else {
                 throw new Error(data.detail || "Failed to join");
             }
        }
    } catch (err) {
        showNotification(err.message, 'error');
        btn.textContent = originalText;
        btn.disabled = false;
    }
};

function setupSearch() {
    // Search functionality
    const searchInput = document.querySelector('.search-box input');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const groups = document.querySelectorAll('.group-card');
        
        groups.forEach(group => {
            const title = group.querySelector('h3').textContent.toLowerCase();
            const description = group.querySelector('p').textContent.toLowerCase();
            
            if (title.includes(searchTerm) || description.includes(searchTerm)) {
                group.style.display = 'flex';
                group.style.animation = 'none';
                setTimeout(() => {
                    group.style.animation = 'fadeIn 0.5s ease';
                }, 10);
            } else {
                group.style.display = 'none';
            }
        });
    });
}

function setupCreateGroup() {
    const btn = document.getElementById('createGroupBtn');
    if (btn) {
        btn.addEventListener('click', createNewGroup);
    }
}

async function createNewGroup() {
    const name = prompt("Enter Group Name:");
    if (!name || !name.trim()) return;
    
    const description = prompt("Enter Group Description:");
    
    try {
        const res = await fetch(`${API_URL}/groups/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                description: description || ""
            })
        });
        
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Failed to create group");
        }
        
        showNotification("Group created successfully!", "success");
        loadGroups(); // Reload list
        
    } catch (err) {
        showNotification(err.message, "error");
    }
}

// Notification function
function showNotification(message) {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
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
    
    // Add notification styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Auto-remove notification
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}