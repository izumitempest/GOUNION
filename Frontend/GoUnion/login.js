const API_URL = "http://127.0.0.1:8001";

const emailInput = document.getElementById("email");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("submitBtn");
const errorText = document.getElementById("error");
const toggleBtn = document.getElementById("toggleBtn");
const formTitle = document.getElementById("formTitle");
const toggleMessage = document.getElementById("toggleMessage");

let isLogin = true;

// Toggle between Login and Signup
toggleBtn.addEventListener("click", (e) => {
    e.preventDefault();
    isLogin = !isLogin;
    
    if (isLogin) {
        formTitle.textContent = "GoUnion Login";
        submitBtn.textContent = "Login";
        usernameInput.style.display = "none";
        toggleMessage.textContent = "Don't have an account?";
        toggleBtn.textContent = "Sign Up";
    } else {
        formTitle.textContent = "Create Account";
        submitBtn.textContent = "Sign Up";
        usernameInput.style.display = "block";
        toggleMessage.textContent = "Already have an account?";
        toggleBtn.textContent = "Login";
    }
    errorText.style.display = "none";
});

submitBtn.addEventListener("click", async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const username = usernameInput.value.trim();

    if (!email || !password || (!isLogin && !username)) {
        showError("Please fill in all fields.");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";

    try {
        if (isLogin) {
            await login(email, password);
        } else {
            await signup(email, username, password);
        }
    } catch (err) {
        showError(err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = isLogin ? "Login" : "Sign Up";
    }
});

async function login(email, password) {
    // OAuth2 expects form data, not JSON
    const formData = new URLSearchParams();
    formData.append("username", email); // Supabase uses email as username for auth
    formData.append("password", password);

    const response = await fetch(`${API_URL}/token`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Login failed");
    }

    // Save token
    localStorage.setItem("access_token", data.access_token);
    
    // Redirect
    window.location.href = "home.html";
}

async function signup(email, username, password) {
    const response = await fetch(`${API_URL}/users/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: email,
            username: username,
            password: password
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Signup failed");
    }

    // Auto login after signup
    await login(email, password);
}

function showError(msg) {
    errorText.textContent = msg;
    errorText.style.display = "block";
}
