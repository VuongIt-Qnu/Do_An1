// URL backend
const baseUrl = "http://localhost:8080/api/auth";

// REGISTER
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fullName = document.getElementById("fullName").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const phone = document.getElementById("regPhone").value.trim();
    const password = document.getElementById("regPassword").value;
    const confirm = document.getElementById("regConfirm").value;

    const msg = document.getElementById("registerMessage");
    msg.style.display = "none";

    if (password !== confirm) {
      msg.textContent = "Mật khẩu nhập lại không khớp!";
      msg.classList.add("error");
      msg.style.display = "block";
      return;
    }

    try {
      const res = await fetch(`${baseUrl}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fullName, email, phone, password }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.message || "Đăng ký thất bại");
      }

      msg.textContent = data.message || "Đăng ký thành công!";
      msg.classList.remove("error");
      msg.style.display = "block";

      // ví dụ: chuyển sang login sau 1.5s
      // setTimeout(() => (window.location.href = "login.html"), 1500);
    } catch (err) {
      msg.textContent = err.message;
      msg.classList.add("error");
      msg.style.display = "block";
    }
  });
}

// LOGIN
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const msg = document.getElementById("loginMessage");
    msg.style.display = "none";

    try {
      const res = await fetch(`${baseUrl}/login`, {   // dùng lại baseUrl
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.message || "Login thất bại");
      }

      msg.textContent = "Login thành công";
      msg.classList.remove("error");
      msg.style.display = "block";

      // Lưu token nếu AuthResponse có accessToken
      if (data.accessToken) {
        localStorage.setItem("token", data.accessToken);
      }

      // TODO: chuyển qua trang Home
      // window.location.href = "/home.html";
    } catch (err) {
      msg.textContent = err.message;
      msg.classList.add("error");
      msg.style.display = "block";
    }
  });
}
