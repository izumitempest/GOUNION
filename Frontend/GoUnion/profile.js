const API_URL = "http://127.0.0.1:8001";
const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

const toggleBtn = document.getElementById("toggleBtn");
const sidebar = document.getElementById("sidebar");
const profileForm = document.getElementById("profileForm");
const saveBtn = document.getElementById("saveBtn");

// Sidebar toggle
toggleBtn.addEventListener("click", () => {
    sidebar.style.left = sidebar.style.left === "0px" ? "-260px" : "0px";
});

// Load user profile
async function loadProfile() {
    try {
        const res = await fetch(`${API_URL}/users/me/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const user = await res.json();
        
        document.getElementById("username").value = user.username;
        document.getElementById("email").value = user.email;
        
        if (user.profile) {
            document.getElementById("bio").value = user.profile.bio || "";
            document.getElementById("university").value = user.profile.university || "";
            document.getElementById("course").value = user.profile.course || "";
            document.getElementById("graduation_year").value = user.profile.graduation_year || "";
        }
    } catch (err) {
        console.error("Failed to load profile:", err);
    }
}

// Save profile
profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";
    
    try {
        const res = await fetch(`${API_URL}/profiles/me`, {
            method: "PUT",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                bio: document.getElementById("bio").value,
                university: document.getElementById("university").value,
                course: document.getElementById("course").value,
                graduation_year: parseInt(document.getElementById("graduation_year").value) || null
            })
        });
        
        if (res.ok) {
            alert("Profile updated successfully!");
        } else {
            alert("Failed to update profile");
        }
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Save Changes";
    }
});

loadProfile();
