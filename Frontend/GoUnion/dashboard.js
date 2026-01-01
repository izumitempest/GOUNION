const API_URL = "http://127.0.0.1:8001";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

// Navigation toggle
function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
    
    const menuToggle = document.querySelector('.menu-toggle');
    if (navLinks.classList.contains('active')) {
        menuToggle.innerHTML = '✕';
        menuToggle.style.transform = 'rotate(180deg)';
    } else {
        menuToggle.innerHTML = '☰';
        menuToggle.style.transform = 'rotate(0)';
    }
}

// Close menu when clicking outside
document.addEventListener('click', function(event) {
    const navLinks = document.getElementById('navLinks');
    const menuToggle = document.querySelector('.menu-toggle');
    
    if (!navLinks.contains(event.target) && !menuToggle.contains(event.target)) {
        navLinks.classList.remove('active');
        menuToggle.innerHTML = '☰';
        menuToggle.style.transform = 'rotate(0)';
    }
});

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Update time of day greeting
    updateGreeting();
    
    // Update current date
    updateCurrentDate();
    
    // Load user data
    loadUserData();
    
    // Load feed posts
    loadFeedPosts();
    
    // Load notifications
    loadNotifications();
    
    // Setup event listeners
    setupEventListeners();
});

// Update greeting based on time of day
function updateGreeting() {
    const hour = new Date().getHours();
    const timeOfDayEl = document.getElementById('timeOfDay');
    
    if (hour < 12) {
        timeOfDayEl.textContent = 'Morning';
    } else if (hour < 17) {
        timeOfDayEl.textContent = 'Afternoon';
    } else {
        timeOfDayEl.textContent = 'Evening';
    }
}

// Update current date
function updateCurrentDate() {
    const dateEl = document.getElementById('currentDate');
    const now = new Date();
    
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    
    dateEl.textContent = now.toLocaleDateString('en-US', options);
}

// Load user data
async function loadUserData() {
    try {
        const res = await fetch(`${API_URL}/users/me/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to load user");
        
        const user = await res.json();
        
        // Update welcome message
        const usernameEl = document.querySelector('.username');
        if (usernameEl) {
            usernameEl.textContent = user.username + '!';
        }
        
        // Update avatar
        const avatarEl = document.querySelector('.user-avatar');
        const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjOGI1Y2Y2IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSI4IiByPSI0Ij48L2NpcmNsZT48cGF0aCBkPSJNMjAgMjF2LTIgYS00IDQtMCAwIDAtNC00IEggOCBhLTQgNC0wIDAtMC00IDQgdiAyIj48L3BhdGg+PC9zdmc+';
        
        if (avatarEl) {
            avatarEl.src = (user.profile && user.profile.profile_picture) ? user.profile.profile_picture : defaultAvatar;
        }
        
        // Load sidebar groups
        loadSidebarGroups();
        
    } catch (err) {
        console.error("Error loading user:", err);
    }
}

async function loadSidebarGroups() {
    const list = document.getElementById('sidebarGroups');
    if (!list) return;
    
    try {
        const res = await fetch(`${API_URL}/groups/?limit=3`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to load groups");
        
        const groups = await res.json();
        list.innerHTML = '';
        
        if (groups.length === 0) {
            list.innerHTML = '<div style="padding: 1rem; color: #b0b0c0; text-align: center;">No groups found</div>';
            return;
        }
        
        groups.forEach(group => {
            const item = document.createElement('div');
            item.className = 'group-item';
            // Mock image based on group name
            const initial = group.name.charAt(0).toUpperCase();
            
            // Re-using styles from home.html structure
            item.innerHTML = `
                <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #6d28d9, #8b5cf6); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">${initial}</div>
                <div class="group-info">
                    <h4>${group.name}</h4>
                    <p>${group.members_count || 0} members</p>
                </div>
                <a href="groups.html" style="color: #b0b0c0;"><i class="fas fa-chevron-right"></i></a>
            `;
            list.appendChild(item);
        });
        
    } catch (err) {
        console.error("Sidebar groups error:", err);
        list.innerHTML = '<div style="padding: 1rem; color: #ef4444; text-align: center;">Failed to load</div>';
    }
}

// Load feed posts
async function loadFeedPosts() {
    const feedContainer = document.getElementById('feedContainer');
    
    try {
        // Using /posts/ instead of /feed/ to show global activity for now
        const res = await fetch(`${API_URL}/posts/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to load feed");
        
        const posts = await res.json();
        
        feedContainer.innerHTML = '';
        
        if (posts.length === 0) {
            feedContainer.innerHTML = '<div class="no-posts">No posts yet. Follow someone or join a group!</div>';
            return;
        }

        posts.forEach(post => {
            const postElement = createPostElement(post);
            feedContainer.appendChild(postElement);
        });
    } catch (err) {
        console.error("Error loading feed:", err);
        feedContainer.innerHTML = '<div class="error-posts">Failed to load feed.</div>';
    }
}

// Create post element
function createPostElement(post) {
    const postEl = document.createElement('div');
    postEl.className = 'post-card';
    
    // Fallbacks for missing data
    // Use a generic SVG data URI for missing avatars instead of external placeholder
    const defaultAvatar = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjOGI1Y2Y2IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PGNpcmNsZSBjeD0iMTIiIGN5PSI4IiByPSI0Ij48L2NpcmNsZT48cGF0aCBkPSJNMjAgMjF2LTIgYS00IDQtMCAwIDAtNC00IEggOCBhLTQgNC0wIDAgMC00IDQgdiAyIj48L3BhdGg+PC9zdmc+';
    
    const userAvatar = post.user?.profile?.profile_picture || defaultAvatar;
    const userName = post.user?.username || '';
    const postImage = post.image; 
    const isLiked = false; // TODO: Check if current user liked
    
    postEl.innerHTML = `
        <div class="post-header">
            <div class="post-user">
                <img src="${userAvatar}" alt="${userName}" class="post-avatar">
                <div>
                    <h4>${userName}</h4>
                    <p>Student</p> 
                </div>
            </div>
            <div class="post-meta">
                <span class="post-time">${new Date(post.created_at).toLocaleDateString()}</span>
                <!-- <span class="post-group">General</span> -->
            </div>
        </div>
        <div class="post-content">
            <p>${post.caption || ''}</p>
            ${postImage ? `<img src="${postImage}" alt="Post image" class="post-image">` : ''}
        </div>
        <div class="post-stats">
            <span id="likes-count-${post.id}"><i class="fas fa-heart"></i> ${post.likes_count || 0}</span>
            <span><i class="fas fa-comment"></i> ${post.comments ? post.comments.length : 0}</span>
            <span><i class="fas fa-share"></i> Share</span>
        </div>
        <div class="post-actions">
            <button class="post-action-btn like-btn ${isLiked ? 'active' : ''}" onclick="likePost(${post.id})">
                <i class="far fa-heart"></i> Like
            </button>
            <button class="post-action-btn comment-btn" onclick="commentOnPost(${post.id})">
                <i class="far fa-comment"></i> Comment
            </button>
            <button class="post-action-btn share-btn" onclick="sharePost(${post.id})">
                <i class="fas fa-share"></i> Share
            </button>
        </div>
    `;
    
    return postEl;
}

// Create new post
async function createNewPost() {
    const postContent = document.getElementById('postContent').value;
    const imageInput = document.getElementById('postImage');
    const postBtn = document.getElementById('postBtn');
    
    if (!postContent.trim()) {
        showNotification('Please write something to post!', 'error');
        return;
    }
    
    postBtn.disabled = true;
    postBtn.textContent = 'Posting...';

    try {
        let imageUrl = null;
        
        // Upload image first if exists
        if (imageInput.files[0]) {
             const formData = new FormData();
             formData.append("file", imageInput.files[0]);
             
             const uploadRes = await fetch(`${API_URL}/upload/`, { 
                method: "POST", 
                headers: { "Authorization": `Bearer ${token}` },
                body: formData 
            });
            
            if (uploadRes.ok) {
                const data = await uploadRes.json();
                imageUrl = data.url;
            } else {
                 console.error("Image upload failed");
            }
        }

        const res = await fetch(`${API_URL}/posts/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                caption: postContent,
                image: imageUrl
            })
        });

        if (!res.ok) throw new Error("Failed to create post");
        
        const newPost = await res.json();
        
        // Add to feed immediately
        const feedContainer = document.getElementById('feedContainer');
        const postElement = createPostElement(newPost);
        feedContainer.insertBefore(postElement, feedContainer.firstChild); // Prepend
        
        // Clear form
        document.getElementById('postContent').value = '';
        imageInput.value = '';
        showNotification('Post published successfully!', 'success');
        
    } catch (err) {
        showNotification(err.message, 'error');
    } finally {
        postBtn.disabled = false;
        postBtn.textContent = 'Post';
    }
}

// Load notifications
async function loadNotifications() {
    const notificationsList = document.querySelector('.notifications-list');
    
    try {
        const res = await fetch(`${API_URL}/notifications/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to load notifications");
        
        const notifications = await res.json();
        
        notificationsList.innerHTML = '';
        
        if (notifications.length === 0) {
            notificationsList.innerHTML = '<div class="no-notifs">No new notifications</div>';
            return;
        }
        
        // Update badge count
        const notifCountEl = document.querySelector('.notification-count');
        const unreadCount = notifications.filter(n => !n.is_read).length;
        if (notifCountEl) {
            notifCountEl.textContent = unreadCount;
            notifCountEl.style.display = unreadCount > 0 ? 'flex' : 'none';
        }

        notifications.forEach(notif => {
            const notifEl = document.createElement('div');
            notifEl.className = `notification-item ${notif.is_read ? 'read' : 'unread'}`;
            // Simple mapping for demo
            let message = '';
            if (notif.type === 'like') message = 'liked your post';
            else if (notif.type === 'comment') message = 'commented on your post';
            else if (notif.type === 'friend_request') message = 'sent you a friend request';
            else if (notif.type === 'follow') message = 'started following you';
            else message = 'New notification';

            notifEl.innerHTML = `
                <div class="notification-content">
                    <p><strong>${notif.sender_id}</strong> ${message}</p>
                    <span class="notification-time">${new Date(notif.created_at).toLocaleDateString()}</span>
                </div>
                ${!notif.is_read ? '<span class="notification-dot"></span>' : ''}
            `;
            notificationsList.appendChild(notifEl);
        });
    } catch (err) {
        console.error("Error loading notifications:", err);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Post button
    const postBtn = document.getElementById('postBtn');
    if (postBtn) {
        postBtn.addEventListener('click', createNewPost);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterFeed(this.textContent);
        });
    });
}

// Filter feed
function filterFeed(filter) {
    const feedContainer = document.getElementById('feedContainer');
    const posts = feedContainer.querySelectorAll('.post-card');
    
    posts.forEach(post => {
        const group = post.querySelector('.post-group').textContent;
        
        switch(filter) {
            case 'All':
                post.style.display = 'block';
                break;
            case 'Following':
                // Logic for following filter
                post.style.display = 'block';
                break;
            case 'Groups':
                // Logic for groups filter
                post.style.display = 'block';
                break;
        }
    });
}

// Quick actions
function quickPost() {
    document.getElementById('postContent').focus();
    showNotification('Start typing your post!', 'info');
}

function joinGroup() {
    window.location.href = 'groups.html';
}

function findFriends() {
    showNotification('Search for friends feature coming soon!', 'info');
}

function viewEvents() {
    showNotification('Events page coming soon!', 'info');
}

// Post interactions
async function likePost(postId) {
    try {
        const res = await fetch(`${API_URL}/posts/${postId}/like`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            showNotification(data.status === 'liked' ? 'Post liked!' : 'Post unliked', 'success');
            
            // Update count UI
            document.getElementById(`likes-count-${postId}`).innerHTML = `<i class="fas fa-heart"></i> ${data.likes_count}`;
        }
    } catch (err) {
        console.error("Like failed", err);
    }
}

// Comment System
let currentPostIdForComments = null;

async function commentOnPost(postId) {
    currentPostIdForComments = postId;
    createCommentModal(); // Ensure modal exists
    
    const modal = document.getElementById('commentModal');
    const commentsList = document.getElementById('commentsList');
    
    // Show modal
    modal.style.display = 'flex';
    commentsList.innerHTML = '<div class="loading-comments">Loading discussion...</div>';
    
    try {
        const res = await fetch(`${API_URL}/posts/${postId}/comments`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) throw new Error("Failed to load comments");
        
        const comments = await res.json();
        renderComments(comments);
        
    } catch (err) {
        commentsList.innerHTML = '<div class="error-comments">Failed to load comments</div>';
    }
}

function renderComments(comments) {
    const list = document.getElementById('commentsList');
    list.innerHTML = '';
    
    if (comments.length === 0) {
        list.innerHTML = '<div class="no-comments">No comments yet. Be the first!</div>';
        return;
    }
    
    comments.forEach(comment => {
        const div = document.createElement('div');
        div.className = 'comment-item';
        // Note: comment.user is nested in schema
        const username = comment.user ? comment.user.username : 'Unknown';
        
        div.innerHTML = `
            <div class="comment-avatar">${username.charAt(0).toUpperCase()}</div>
            <div class="comment-body">
                <div class="comment-header">
                    <span class="comment-user">${username}</span>
                    <span class="comment-time">${new Date(comment.created_at).toLocaleDateString()}</span>
                </div>
                <p>${comment.content}</p>
            </div>
        `;
        list.appendChild(div);
    });
}

async function submitComment() {
    const input = document.getElementById('newCommentText');
    const content = input.value.trim();
    if (!content) return;
    
    const btn = document.getElementById('sendCommentBtn');
    btn.disabled = true;
    
    try {
        const res = await fetch(`${API_URL}/posts/${currentPostIdForComments}/comments/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ content: content })
        });
        
        if (!res.ok) throw new Error("Failed to post comment");
        
        // Refresh comments
        input.value = '';
        commentOnPost(currentPostIdForComments);
        
        // Update feed count
        // Note: Ideally update local DOM directly to avoid reload
        
    } catch (err) {
        showNotification(err.message, 'error');
    } finally {
        btn.disabled = false;
        input.focus();
    }
}

function createCommentModal() {
    if (document.getElementById('commentModal')) return;
    
    const modal = document.createElement('div');
    modal.id = 'commentModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-container">
            <div class="modal-header">
                <h3>Comments</h3>
                <button onclick="document.getElementById('commentModal').style.display='none'" class="close-modal">&times;</button>
            </div>
            <div id="commentsList" class="modal-body"></div>
            <div class="modal-footer">
                <input type="text" id="newCommentText" placeholder="Write a comment..." onkeypress="if(event.key==='Enter') submitComment()">
                <button id="sendCommentBtn" onclick="submitComment()"><i class="fas fa-paper-plane"></i></button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });
}

function sharePost(postId) {
    showNotification('Share feature coming soon!', 'info');
    // In real app, open share modal
}

// Notifications
function showNotifications() {
    const panel = document.getElementById('notificationsPanel');
    panel.classList.add('active');
}

function hideNotifications() {
    const panel = document.getElementById('notificationsPanel');
    panel.classList.remove('active');
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        showNotification('Logging out...', 'info');
        setTimeout(() => {
            window.location.href = 'login.html'; // Redirect to login page
        }, 1000);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification-toast');
    if (existing) existing.remove();
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification-toast ${type}`;
    notification.innerHTML = `
        <div class="notification-icon">
            ${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}
        </div>
        <div class="notification-message">${message}</div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Add CSS for posts and notifications
const style = document.createElement('style');
style.textContent = `
    .post-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        animation: fadeIn 0.5s ease;
    }
    
    .post-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .post-user {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .post-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #8b5cf6;
    }
    
    .post-user h4 {
        color: #ffffff;
        font-size: 1rem;
        margin-bottom: 0.2rem;
    }
    
    .post-user p {
        color: #b0b0c0;
        font-size: 0.85rem;
    }
    
    .post-meta {
        text-align: right;
    }
    
    .post-time {
        display: block;
        color: #8b5cf6;
        font-size: 0.85rem;
        margin-bottom: 0.2rem;
    }
    
    .post-group {
        display: block;
        color: #b0b0c0;
        font-size: 0.85rem;
        background: rgba(139, 92, 246, 0.1);
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
    }
    
    .post-content {
        margin-bottom: 1rem;
    }
    
    .post-content p {
        color: #e0e0e0;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .post-image {
        width: 100%;
        border-radius: 12px;
        max-height: 400px;
        object-fit: cover;
    }
    
    .post-stats {
        display: flex;
        gap: 1.5rem;
        color: #b0b0c0;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .post-stats span {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: color 0.3s ease;
    }
    
    .post-stats span:hover {
        color: #8b5cf6;
    }
    
    .post-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .post-action-btn {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #b0b0c0;
        padding: 0.8rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .post-action-btn:hover {
        background: rgba(109, 40, 217, 0.15);
        color: #ffffff;
        border-color: #8b5cf6;
        transform: translateY(-2px);
    }
    
    .notification-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        margin-bottom: 0.8rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .notification-item:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    .notification-item.unread {
        background: rgba(109, 40, 217, 0.1);
    }
    
    .notification-content p {
        color: #ffffff;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
    }
    
    .notification-time {
        color: #b0b0c0;
        font-size: 0.8rem;
    }
    
    .notification-dot {
        width: 8px;
        height: 8px;
        background: #8b5cf6;
        border-radius: 50%;
    }
    
    .notification-toast {
        position: fixed;
        bottom: 100px;
        right: 20px;
        background: rgba(25, 25, 35, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .notification-toast.success {
        border-left: 4px solid #10b981;
    }
    
    .notification-toast.error {
        border-left: 4px solid #ef4444;
    }
    
    .notification-toast.info {
        border-left: 4px solid #8b5cf6;
    }
    
    .notification-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    
    .notification-toast.success .notification-icon {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
    }
    
    .notification-toast.error .notification-icon {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    .notification-toast.info .notification-icon {
        background: rgba(139, 92, 246, 0.2);
        color: #8b5cf6;
    }
    
    .notification-message {
        color: #ffffff;
        flex: 1;
    }
    
    .notification-close {
        background: transparent;
        border: none;
        color: #b0b0c0;
        cursor: pointer;
        font-size: 1rem;
        transition: color 0.3s ease;
    }
    
    .notification-close:hover {
        color: #ffffff;
    }

    /* Comment Modal Styles */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(5px);
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        animation: fadeIn 0.2s ease;
    }

    .modal-container {
        background: #1a1a24;
        width: 100%;
        max-width: 500px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        flex-direction: column;
        max-height: 80vh;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    .modal-header {
        padding: 1.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .modal-header h3 {
        margin: 0;
        color: white;
    }

    .close-modal {
        background: none;
        border: none;
        color: #b0b0c0;
        font-size: 1.5rem;
        cursor: pointer;
    }

    .modal-body {
        padding: 1.5rem;
        overflow-y: auto;
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .modal-footer {
        padding: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        gap: 1rem;
    }

    .modal-footer input {
        flex: 1;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.8rem 1rem;
        border-radius: 20px;
        color: white;
    }

    .modal-footer button {
        background: #8b5cf6;
        color: white;
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .comment-item {
        display: flex;
        gap: 1rem;
        animation: slideIn 0.3s ease;
    }

    .comment-avatar {
        width: 35px;
        height: 35px;
        background: linear-gradient(135deg, #6d28d9, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        flex-shrink: 0;
    }

    .comment-body {
        background: rgba(255, 255, 255, 0.03);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        flex: 1;
    }

    .comment-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.3rem;
    }

    .comment-user {
        color: white;
        font-weight: 500;
        font-size: 0.9rem;
    }

    .comment-time {
        color: #b0b0c0;
        font-size: 0.75rem;
    }

    .comment-body p {
        margin: 0;
        color: #e0e0e0;
        font-size: 0.95rem;
    }
`;
document.head.appendChild(style);

// Close notifications when clicking outside
document.addEventListener('click', function(event) {
    const panel = document.getElementById('notificationsPanel');
    const bell = document.querySelector('.notification-bell');
    
    if (panel && panel.classList.contains('active') && 
        !panel.contains(event.target) && 
        !bell.contains(event.target)) {
        hideNotifications();
    }
});

// Simulate real-time updates
setInterval(() => {
    // Update online status randomly
    const onlineCount = Math.floor(Math.random() * 5) + 10;
    const onlineCountEl = document.querySelector('.online-count');
    if (onlineCountEl) {
        onlineCountEl.textContent = onlineCount;
    }
    
    // Update notification count
    const notifCount = Math.floor(Math.random() * 5);
    const notifCountEl = document.querySelector('.notification-count');
    if (notifCountEl) {
        notifCountEl.textContent = notifCount;
    }
}, 30000); // Every 30 seconds

// Initialize with animations
setTimeout(() => {
    document.body.style.opacity = '1';
}, 100);

// Post Tool Functions
function addImage() {
    document.getElementById('postImage').click();
}

function addVideo() {
    showNotification('Video upload coming soon!', 'info');
}

function addPoll() {
    showNotification('Polls coming soon!', 'info');
}

function tagFriends() {
    showNotification('Tagging friends coming soon!', 'info');
}