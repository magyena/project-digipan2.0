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
    
//currentdate
document.addEventListener('DOMContentLoaded', function () {
    // Dapatkan elemen yang ingin diperbarui
    var dateElement = document.querySelector('.date-span');
    
    if (dateElement) {
      // Format tanggal saat ini
      var now = new Date();
      var options = { year: 'numeric', month: 'long', day: 'numeric' };
      var formattedDate = now.toLocaleDateString(undefined, options);
      
      // Perbarui teks elemen
      dateElement.textContent = formattedDate;
    }
});
 document.getElementById('view-more').addEventListener('click', function(event) {
    event.preventDefault();
    
    var moreMessages = document.querySelector('.more-messages');
    
    if (moreMessages.style.display === 'none' || moreMessages.style.display === '') {
        moreMessages.style.display = 'block';
        this.innerHTML = 'Tampilkan lebih sedikit <i class="fas fa-chevron-up"></i>'; // Update text and icon
    } else {
        moreMessages.style.display = 'none';
        this.innerHTML = 'Tampilkan lebih banyak <i class="fas fa-chevron-right"></i>'; // Update text and icon
    }
});

document.querySelectorAll('.customer-message').forEach(function(item) {
    item.addEventListener('click', function(event) {
        var messageContent = this.querySelector('.message-title').textContent;
        var messageUser = this.querySelector('.message-time').textContent.split(' · ')[0]; // Ambil user dari format text
        var messageTimestamp = this.querySelector('.message-time').textContent.split(' · ')[1]; // Ambil timestamp dari format text

        // Isi modal dengan data pesan
        document.getElementById('message-content').textContent = messageContent;
        document.getElementById('message-user').textContent = "User: " + messageUser;
        document.getElementById('message-timestamp').textContent = "Received at: " + messageTimestamp;

        // Tampilkan modal
        $('#messageModal').modal('show');
    });
});

 document.getElementById('read-more-messages').addEventListener('click', function(event) {
        event.preventDefault(); // Mencegah tindakan default dari link
        document.getElementById('messages-section').scrollIntoView({
            behavior: 'smooth' // Menyediakan efek gulir yang halus
        });
 });
    
 