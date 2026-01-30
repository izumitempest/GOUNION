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
// Profile State
let profileData = {
    profile_picture: null,
    cover_photo: null
};

// Image Upload Handler
async function handleImageUpload(file) {
    const formData = new FormData();
    formData.append("file", file);
    
    try {
        const res = await fetch(`${API_URL}/upload/`, { 
            method: "POST", 
            headers: { "Authorization": `Bearer ${token}` },
            body: formData 
        });
        
        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`Server responded with ${res.status}: ${errorText}`);
        }

        const data = await res.json();
        return data.url;
    } catch (err) {
        console.error("Upload failed", err);
        alert(`Failed to upload image: ${err.message}`);
        return null;
    }
}

// Avatar Input
document.getElementById("avatarInput").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
        const url = await handleImageUpload(file);
        if (url) {
            profileData.profile_picture = url;
            document.getElementById("avatarPreview").src = url;
        }
    }
});

// Cover Input
document.getElementById("coverInput").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (file) {
        const url = await handleImageUpload(file);
        if (url) {
            profileData.cover_photo = url;
            document.getElementById("coverPreview").src = url;
        }
    }
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
            document.getElementById("hometown").value = user.profile.hometown || "";
            document.getElementById("relationship_status").value = user.profile.relationship_status || "";
            
            // Images
            if (user.profile.profile_picture) {
                profileData.profile_picture = user.profile.profile_picture;
                document.getElementById("avatarPreview").src = user.profile.profile_picture;
            }
            if (user.profile.cover_photo) {
                profileData.cover_photo = user.profile.cover_photo;
                document.getElementById("coverPreview").src = user.profile.cover_photo;
                document.getElementById("coverPreview").style.display = "block";
            }
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
        const payload = {
            bio: document.getElementById("bio").value,
            university: document.getElementById("university").value,
            course: document.getElementById("course").value,
            graduation_year: parseInt(document.getElementById("graduation_year").value) || null,
            hometown: document.getElementById("hometown").value,
            relationship_status: document.getElementById("relationship_status").value,
            profile_picture: profileData.profile_picture,
            cover_photo: profileData.cover_photo
        };

        const res = await fetch(`${API_URL}/profiles/me`, {
            method: "PUT",
            headers: { 
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            alert("Profile updated successfully!");
        } else {
            const errData = await res.json();
            alert("Failed to update profile: " + (errData.detail || "Unknown error"));
        }
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Save Changes";
    }
});

loadProfile();
