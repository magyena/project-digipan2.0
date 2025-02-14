 // Mengambil data pengeluaran dari API
function fetchPengeluaran(bulan = '', tahun = '') {
    let url = '/api/pengeluaran';
    if (bulan || tahun) {
        url += `?bulan=${bulan}&tahun=${tahun}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('pengeluaran-ul');
            tableBody.innerHTML = ''; // Reset tabel sebelum menampilkan data baru

            // Menampilkan pengeluaran di tabel
            if (data.pengeluaran_data.length > 0) {
                data.pengeluaran_data.forEach(pengeluaran => {
                    const tr = document.createElement('tr');
                    tr.style.borderBottom = '1px solid #ddd';

                    const tdNamaKegiatan = document.createElement('td');
                    tdNamaKegiatan.style.padding = '10px';
                    tdNamaKegiatan.textContent = pengeluaran.nama_kegiatan;
                    tr.appendChild(tdNamaKegiatan);

                    const tdJumlah = document.createElement('td');
                    tdJumlah.style.padding = '10px';
                    tdJumlah.textContent = `Rp ${pengeluaran.jumlah.toLocaleString()}`;
                    tr.appendChild(tdJumlah);

                    tableBody.appendChild(tr);
                });
            } else {
                const tr = document.createElement('tr');
                const td = document.createElement('td');
                td.setAttribute('colspan', '2');
                td.style.textAlign = 'center';
                td.style.color = 'gray';
                td.textContent = 'Tidak ada data pengeluaran.';
                tr.appendChild(td);
                tableBody.appendChild(tr);
            }

            // Menampilkan total pengeluaran dan total kas di samping judul modal
            const totalPengeluaran = document.getElementById('total-pengeluaran');
            const totalKas = document.getElementById('total-kas');

            totalPengeluaran.textContent = `Rp ${data.total_pengeluaran.toLocaleString()}`;
            totalKas.textContent = `Rp ${data.total_iuran.toLocaleString()}`; // Menggunakan total_iuran
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Menampilkan modal saat tombol diklik
document.getElementById('showPengeluaranBtn').addEventListener('click', function () {
    document.getElementById('pengeluaranModal').style.display = 'block';
    fetchPengeluaran(); // Ambil data tanpa filter saat modal dibuka
});

// Menutup modal saat tombol 'Tutup' diklik
document.getElementById('closeModalBtn').addEventListener('click', function () {
    document.getElementById('pengeluaranModal').style.display = 'none';
});

// Menambahkan event listener untuk filter
const filterBtn = document.getElementById('filterBtn');
filterBtn.addEventListener('click', function () {
    const bulan = document.getElementById('filter-bulan').value;
    const tahun = document.getElementById('filter-tahun').value;
    fetchPengeluaran(bulan, tahun); // Ambil data dengan filter bulan dan tahun
});


        //  //hide klik kanan
// document.addEventListener("contextmenu", function(e){
//     e.preventDefault();
// }, false);

// document.onkeydown = function(e) {
//     if(e.key == 'F12' || (e.ctrlKey && e.shiftKey && e.key == 'I')) {
//         e.preventDefault();
//     }
// };

// Tampilkan splash screen selama 3 detik
        window.addEventListener("load", function() {
            const splash = document.getElementById('splashScreen');
            const mainContent = document.getElementById('mainContent');
            
            setTimeout(() => {
                splash.classList.add('hidden'); // Hilangkan splash screen dengan animasi
                mainContent.style.display = 'grid'; // Tampilkan konten utama
            }, 3000); // Ganti waktu di sini (dalam milidetik)
        });
       

        // Ambil elemen modal dan tombol
    const openTutorialBtn = document.getElementById('openTutorialBtn');
    const tutorialModal = document.getElementById('tutorialModal');
    const closeTutorialBtn = document.getElementById('closeTutorialBtn');
    const tutorialIframe = document.getElementById('tutorialIframe');

    // Fungsi untuk membuka modal
    openTutorialBtn.onclick = function() {
        tutorialModal.style.display = 'flex';
    }

    // Fungsi untuk menutup modal dan menghentikan video
    closeTutorialBtn.onclick = function() {
        tutorialModal.style.display = 'none';
        stopYouTubeVideo();
    }

    // Menutup modal jika klik di luar area modal
    window.onclick = function(event) {
        if (event.target === tutorialModal) {
            tutorialModal.style.display = 'none';
            stopYouTubeVideo();
        }
    }

    // Fungsi untuk menghentikan video YouTube
    function stopYouTubeVideo() {
        const iframeSrc = tutorialIframe.src; // Simpan URL asli
        tutorialIframe.src = ''; // Kosongkan src untuk menghentikan video
        tutorialIframe.src = iframeSrc; // Setel ulang src ke URL asli
    }

    const lastUpdateDate = document.getElementById('last-update-date');
const currentDate = new Date().toLocaleString(); // Mendapatkan tanggal dan waktu saat ini
lastUpdateDate.textContent = currentDate;


// Fungsi untuk toggle sidebar
    function toggleSidebar() {
        var sidebar = document.getElementById("sidebar");
        var mainContent = document.getElementById("mainContent");

        if (sidebar.classList.contains("expanded")) {
            sidebar.classList.remove("expanded");
            mainContent.classList.add("expanded");
        } else {
            sidebar.classList.add("expanded");
            mainContent.classList.remove("expanded");
        }
    }

    // Menutup sidebar saat klik di luar sidebar
    document.addEventListener('click', function(event) {
        var sidebar = document.getElementById('sidebar');
        var menuToggle = document.querySelector('.menu-toggle');
        
        // Mengecek apakah klik terjadi di luar sidebar dan bukan di tombol menu
        if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
            if (sidebar.classList.contains("expanded")) {
                sidebar.classList.remove("expanded");
                var mainContent = document.getElementById("mainContent");
                mainContent.classList.add("expanded");
            }
        }
    });

    // Menutup sidebar saat menu diklik
    function closeSidebar() {
        var sidebar = document.getElementById("sidebar");
        if (sidebar.classList.contains("expanded")) {
            sidebar.classList.remove("expanded");
            var mainContent = document.getElementById("mainContent");
            mainContent.classList.add("expanded");
        }
    }


    let kegiatanIndex = 0;

function slideKegiatan() {
    const slider = document.querySelector(".kegiatan-slider");
    const slides = document.querySelectorAll(".kegiatan-slider img");
    const totalSlides = slides.length;

    kegiatanIndex++;

    if (kegiatanIndex >= totalSlides) {
        kegiatanIndex = 0;
    }

    const translateValue = -kegiatanIndex * 100 + "%";
    slider.style.transform = "translateX(" + translateValue + ")";

    setTimeout(slideKegiatan, 3000); // Ganti gambar setiap 3 detik
}

// Jalankan slider saat halaman dimuat
document.addEventListener("DOMContentLoaded", slideKegiatan);
