
        function toggleForm(formType) {
            document.getElementById('login-form').classList.toggle('active', formType === 'login');
            document.getElementById('register-form').classList.toggle('active', formType === 'register');
        }

        // Fungsi untuk men-toggle visibilitas password
        function togglePasswordVisibility(inputId) {
            var input = document.getElementById(inputId);
            var icon = input.nextElementSibling;

            if (input.type === "password") {
                input.type = "text";
                icon.classList.remove("fa-eye");
                icon.classList.add("fa-eye-slash");
            } else {
                input.type = "password";
                icon.classList.remove("fa-eye-slash");
                icon.classList.add("fa-eye");
            }
        }
    

document.querySelector("#signUpForm").addEventListener("submit", function(event) {
    event.preventDefault();

    Swal.fire({
        icon:"info",
        title: 'Sedang diproses...',
        text: 'Harap tunggu...',
        showConfirmButton: false,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    let form = event.target;
    let formData = new FormData(form);

    // Pastikan untuk mengirim data dengan benar
    setTimeout(() => {
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                Swal.fire({
                    icon:"success",
                    title: 'Sukses!',
                    text: data.message,
                    confirmButtonText: 'OK'
                });
                form.reset();
            } else if (data.error) {
                Swal.fire({
                    icon:"error",
                    title: 'Terjadi Kesalahan',
                    confirmButtonText: 'Coba Lagi'
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon:"error",
                title: 'Terjadi Kesalahan!',
                text: 'Tidak dapat mengirim data, coba lagi.',
                confirmButtonText: 'Coba Lagi'
            });
        });
    }, 3000); // Jeda 3000 milidetik (3 detik)
});


// Untuk menangani submit form login
document.getElementById("loginuser").addEventListener("submit", function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    Swal.fire({
        title: "Sedang memproses...",
        text: "Harap tunggu...",
        icon:"info",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    // Jeda 3 detik sebelum mengirim data
    setTimeout(() => {
        fetch("/loginusers", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                Swal.fire({
                    icon:"success",
                    title: "Login Berhasil!",
                    text: `Selamat datang, ${data.user}!`,
                    timer: 3000,
                    showConfirmButton: false
                }).then(() => {
                    window.location.href = "/main";
                });
            } else {
                let errorMessage = data.error || "Terjadi kesalahan!";
                Swal.fire({
                    icon:"error",
                    title: "Login Gagal!",
                    text: errorMessage,
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon:"error",
                title: "Terjadi Kesalahan!",
                text: "Gagal menghubungi server.",
            });
        });
    }, 3000); // Jeda 3000 milidetik (3 detik)
});

function togglePasswordVisibility(inputId) {
    var passwordField = document.getElementById(inputId);
    var eyeIcon = passwordField.nextElementSibling; // Mendapatkan ikon mata

    // Cek apakah tipe input saat ini adalah 'password'
    if (passwordField.type === "password") {
        passwordField.type = "text";  // Ubah tipe menjadi 'text' untuk melihat password
        eyeIcon.classList.remove("fa-eye");  // Hapus ikon mata tertutup
        eyeIcon.classList.add("fa-eye-slash");  // Tambahkan ikon mata terbuka
    } else {
        passwordField.type = "password";  // Ubah tipe kembali menjadi 'password'
        eyeIcon.classList.remove("fa-eye-slash");  // Hapus ikon mata terbuka
        eyeIcon.classList.add("fa-eye");  // Tambahkan ikon mata tertutup
    }
}

document.getElementById('nomor_whatsapp').addEventListener('input', function (e) {
        this.value = this.value.replace(/[^0-9]/g, ''); // Menghapus karakter selain angka
});
 
 window.addEventListener('DOMContentLoaded', (event) => {
    // Cek jika ada elemen flash message
    const flashMessage = document.getElementById('flash-message');
    
    if (flashMessage) {
      // Set timer untuk menghilangkan flash message setelah 3 detik
      setTimeout(() => {
        flashMessage.classList.add('fade-out'); // Tambahkan kelas fade-out
      }, 3000); // 3000ms = 3 detik
    }
  });

  function loginAsGuest() {
    window.location.href = "/buku-tamu";  // Mengarahkan ke endpoint Flask
}
function openForgotPasswordModal() {
    const modal = document.getElementById("forgot-password-modal"); // Pastikan ID sesuai
    if (modal) {
        modal.style.display = "flex"; // Pastikan modal terlihat
    } else {
        console.error("Modal tidak ditemukan!");
    }
}

function closeForgotPasswordModal() {
    const modal = document.getElementById("forgot-password-modal");
    if (modal) {
        modal.style.display = "none";
    }
}

// Tutup modal jika klik di luar modal
window.onclick = function(event) {
    const modal = document.getElementById("forgot-password-modal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
};
