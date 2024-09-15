// static/assets/js/main.js
document.addEventListener('DOMContentLoaded', function() {
  // Ambil data keluarga terbaru
  fetch('/api/latest_families')
    .then(response => response.json())
    .then(data => {
      const tableBody = document.getElementById('familyTableBody');
      tableBody.innerHTML = '';

      // Loop melalui data dan tambahkan ke tabel
      data.forEach(family => {
        const row = `
          <tr>
            <td>${family.id}</td>
            <td>${family.nama_keluarga}</td>
            <td>${family.nama}</td>
            <td>${family.hubungan_keluarga}</td>
            <td>${family.nomor_keluarga}</td>
          </tr>
        `;
        tableBody.innerHTML += row;
      });
    })
    .catch(error => console.error('Error fetching family data:', error));
});

//tutup flash login
 $(document).ready(function() {
      // Sembunyikan pesan flash setelah 3 detik (3000 ms)
      setTimeout(function() {
        $('#flash-messages .alert').alert('close');
      }, 3000); // 3000 ms = 3 detik
    });