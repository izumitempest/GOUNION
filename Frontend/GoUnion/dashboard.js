const API_URL = "http://127.0.0.1:8001";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const welcomeMsg = document.getElementById("welcomeMsg");
const logoutBtn = document.getElementById("logoutBtn");
const feedContainer = document.getElementById("feedContainer");
const postBtn = document.getElementById("postBtn");
const postContent = document.getElementById("postContent");
const postImage = document.getElementById("postImage");

// Sidebar Toggle
const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");
toggleBtn.addEventListener("click", () => {
    sidebar.style.left = sidebar.style.left === "0px" ? "-260px" : "0px";
});

// Logout
logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
});

// Load Data
async function init() {
    try {
        await loadUser();
        await loadFeed();
    } catch (err) {
        console.error(err);
        if (err.message.includes("401")) {
            localStorage.removeItem("access_token");
            window.location.href = "login.html";
        }
    }
}

async function loadUser() {
    const res = await fetch(`${API_URL}/users/me/`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) throw new Error(res.status);
    const user = await res.json();
    welcomeMsg.textContent = `Welcome Back, ${user.username}`;
    
    // Log Device Info (Background)
    logDevice();
}

async function loadFeed() {
    // For now, fetch all posts if feed is empty (since we have no friends yet)
    // In production, use /feed/
    let res = await fetch(`${API_URL}/posts/`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    
    const posts = await res.json();
    renderPosts(posts);
}

function renderPosts(posts) {
    console.log("renderPosts called with", posts.length, "posts");
    feedContainer.innerHTML = "";
    if (posts.length === 0) {
        feedContainer.innerHTML = "<p style='text-align:center; color: #71717a;'>No posts yet. Be the first!</p>";
        return;
    }

    posts.forEach(post => {
        const card = document.createElement("div");
        card.className = "card post-card";
        card.id = `post-${post.id}`;
        
        let imageHtml = "";
        if (post.image) {
            // Debug: log the image URL
            console.log("Post image URL:", post.image);
            
            // Handle different URL formats:
            // 1. Full Supabase URL: https://...supabase.co/storage/...
            // 2. Local URL: /media/...
            // 3. Relative path: media/...
            let imageUrl = post.image;
            if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/')) {
                imageUrl = '/' + imageUrl;
            }
            
            imageHtml = `<img src="${imageUrl}" alt="Post Image" onerror="console.error('Failed to load image:', this.src); this.style.display='none'">`;
        }

        card.innerHTML = `
            <div class="post-header">
                <strong>@${post.user ? post.user.username : 'Unknown'}</strong>
                <small>${new Date(post.created_at).toLocaleDateString()}</small>
            </div>
            <p>${post.caption || ""}</p>
            ${imageHtml}
            <div class="post-actions" style="margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
                <button onclick="likePost(${post.id}, this)">❤️ Like (${post.likes_count || 0})</button>
                <button onclick="toggleComments(${post.id})">💬 Comment (${post.comments ? post.comments.length : 0})</button>
            </div>
            <div id="comments-${post.id}" style="display: none; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.05);">
                <div class="comments-list"></div>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <input type="text" id="comment-input-${post.id}" placeholder="Write a comment..." style="flex: 1; padding: 8px 12px; background: #0f0f1e; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #e4e4e7;">
                    <button onclick="addComment(${post.id})" style="padding: 8px 20px;">Post</button>
                </div>
            </div>
        `;
        feedContainer.appendChild(card);
    });
}

// Like Post
async function likePost(postId, button) {
    try {
        const res = await fetch(`${API_URL}/posts/${postId}/like`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            button.textContent = `❤️ Like (${data.likes_count || 0})`;
        }
    } catch (err) {
        console.error("Failed to like post:", err);
    }
}

// Toggle Comments
async function toggleComments(postId) {
    const commentsDiv = document.getElementById(`comments-${postId}`);
    if (commentsDiv.style.display === "none") {
        commentsDiv.style.display = "block";
        await loadComments(postId);
    } else {
        commentsDiv.style.display = "none";
    }
}

// Load Comments
async function loadComments(postId) {
    try {
        const res = await fetch(`${API_URL}/posts/${postId}/comments`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const comments = await res.json();
        
        const commentsList = document.querySelector(`#comments-${postId} .comments-list`);
        commentsList.innerHTML = "";
        
        comments.forEach(comment => {
            const commentEl = document.createElement("div");
            commentEl.style.cssText = "padding: 10px; background: #0f0f1e; border-radius: 8px; margin-bottom: 8px;";
            commentEl.innerHTML = `
                <strong style="color: #667eea;">@${comment.user.username}</strong>
                <p style="margin: 5px 0 0 0; color: #d4d4d8;">${comment.content}</p>
            `;
            commentsList.appendChild(commentEl);
        });
    } catch (err) {
        console.error("Failed to load comments:", err);
    }
}

// Add Comment
async function addComment(postId) {
    const input = document.getElementById(`comment-input-${postId}`);
    const content = input.value.trim();
    
    if (!content) return;
    
    try {
        const res = await fetch(`${API_URL}/posts/${postId}/comments`, {
            method: "POST",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content: content })
        });
        
        if (res.ok) {
            input.value = "";
            await loadComments(postId);
        }
    } catch (err) {
        console.error("Failed to add comment:", err);
    }
}

// Create Post
postBtn.addEventListener("click", async () => {
    const caption = postContent.value;
    const file = postImage.files[0];

    console.log("Creating post - Caption:", caption, "File:", file);

    if (!caption && !file) return;

    postBtn.disabled = true;
    postBtn.textContent = "Posting...";

    try {
        let imagePath = null;
        if (file) {
            console.log("Uploading file:", file.name);
            const formData = new FormData();
            formData.append("file", file);
            const uploadRes = await fetch(`${API_URL}/upload/`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` },
                body: formData
            });
            const uploadData = await uploadRes.json();
            console.log("Upload response:", uploadData);
            imagePath = uploadData.url;
        }

        console.log("Creating post with image:", imagePath);
        const postData = {
            caption: caption,
            image: imagePath
        };
        console.log("Post data:", JSON.stringify(postData));
        
        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        try {
            const res = await fetch(`${API_URL}/posts/`, {
                method: "POST",
                headers: { 
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(postData),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            console.log("Post response status:", res.status);
            const responseData = await res.json();
            console.log("Post response data:", responseData);

            if (res.ok) {
                console.log("Post created successfully:", responseData);
                postContent.value = "";
                postImage.value = "";
                loadFeed(); // Reload feed
            } else {
                console.error("Post creation failed:", res.status, responseData);
                alert(`Failed to create post: ${responseData.detail || JSON.stringify(responseData)}`);
            }
        } catch (fetchError) {
            clearTimeout(timeoutId);
            if (fetchError.name === 'AbortError') {
                console.error("Request timed out");
                alert("Request timed out. Please try again.");
            } else {
                throw fetchError; // Re-throw to outer catch
            }
        }
    } catch (err) {
        console.error("Post creation error:", err);
        console.error("Error stack:", err.stack);
        alert("Failed to post: " + err.message);
    } finally {
        postBtn.disabled = false;
        postBtn.textContent = "Post";
    }
});

// Helper: Log Device
async function logDevice() {
    const ua = navigator.userAgent;
    await fetch(`${API_URL}/users/me/device`, {
        method: "POST",
        headers: { 
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            device_name: "Web Browser",
            device_type: "Desktop",
            browser: ua,
            os_version: navigator.platform
        })
    });
}

init();
