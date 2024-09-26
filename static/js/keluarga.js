// #detail keluarga
//edit dan hapus detail keluarga
$(document).ready(function() {
  var familyData = []; // Tempat menyimpan data keluarga yang diterima dari server

  $('.family-link').on('click', function(e) {
    e.preventDefault();

    var namaKeluarga = $(this).data('nama-keluarga');

    $.ajax({
      url: '/get_family_details/' + encodeURIComponent(namaKeluarga),
      method: 'GET',
      success: function(data) {
        familyData = data; // Simpan data keluarga ke variabel global

        var detailsHtml = '';
        var memberOptionsHtml = '';

        $.each(data, function(index, member) {
          memberOptionsHtml += '<option value="' + member.id + '">' + member.nama + '</option>';

          // Menampilkan detail untuk anggota keluarga
          if (index < 2) { // Tampilkan hanya 2 detail keluarga secara default
            detailsHtml += '<div class="family-detail"><strong>Nama Keluarga:</strong> ' + member.nama_keluarga + '</div>';
            detailsHtml += '<div class="family-detail"><strong>Nama Lengkap:</strong> ' + member.nama + '</div>';
            detailsHtml += '<div class="family-detail"><strong>Tempat Lahir:</strong> ' + member.tempat_lahir + '</div>';
            detailsHtml += '<div class="family-detail"><strong>Tanggal Lahir:</strong> ' + member.tanggal_lahir + '</div>';
            detailsHtml += '<div class="family-detail"><strong>Nomor Keluarga:</strong> ' + member.nomor_keluarga + '</div>';
            var hubunganKeluargaFormatted = member.hubungan_keluarga.replace('_', ' ');
            detailsHtml += '<div class="family-detail"><strong>Hubungan Keluarga:</strong> ' + hubunganKeluargaFormatted + '</div>';
            detailsHtml += '<hr>';
          } else {
            // Menyembunyikan detail yang lebih dari 2
            detailsHtml += '<div class="family-detail d-none"><strong>Nama Keluarga:</strong> ' + member.nama_keluarga + '</div>';
            detailsHtml += '<div class="family-detail d-none"><strong>Nama:</strong> ' + member.nama + '</div>';
            detailsHtml += '<div class="family-detail d-none"><strong>Tempat Lahir:</strong> ' + member.tempat_lahir + '</div>';
            detailsHtml += '<div class="family-detail d-none"><strong>Tanggal Lahir:</strong> ' + member.tanggal_lahir + '</div>';
            detailsHtml += '<div class="family-detail d-none"><strong>Nomor Keluarga:</strong> ' + member.nomor_keluarga + '</div>';
             var hubunganKeluargaFormatted = member.hubungan_keluarga.replace('_', ' ');
            detailsHtml += '<div class="family-detail d-none"><strong>Hubungan Keluarga:</strong> ' + hubunganKeluargaFormatted + '</div>';
            detailsHtml += '<hr>';
          }
        });

        // Menambahkan tombol "Tampilkan Semua" jika ada lebih dari 2 detail
        if (data.length > 2) {
          detailsHtml += '<a href="#" id="show-more" class="btn btn-primary">Tampilkan Semua</a>';
        }

        $('#family-details-content').html(detailsHtml);
        $('#select-family-member').html(memberOptionsHtml);
        $('#edit-family-form').hide(); // Menyembunyikan formulir edit
        $('#family-details-content').show(); // Menampilkan detail keluarga
        $('#familyDetailsModal').modal('show');

        $('#show-more').on('click', function() {
          $('.family-detail.d-none').removeClass('d-none');
          $(this).remove();
          $('#family-details-content').scrollTop($('#family-details-content')[0].scrollHeight);
        });

        $('#select-family-member').on('change', function() {
          var selectedMemberId = $(this).val();
          var selectedMember = familyData.find(member => member.id == selectedMemberId);

          if (selectedMember) {
            $('#edit-nama-keluarga').val(selectedMember.nama_keluarga);
            $('#edit-nama').val(selectedMember.nama);
            $('#edit-tempat-lahir').val(selectedMember.tempat_lahir);
            $('#edit-tanggal-lahir').val(selectedMember.tanggal_lahir);
            $('#edit-nomor-keluarga').val(selectedMember.nomor_keluarga);
            $('#edit-hubungan-keluarga').val(selectedMember.hubungan_keluarga);
            $('#edit-member-id').val(selectedMember.id);
          }
        });

        $('#edit-family').on('click', function() {
          // Menyembunyikan detail dan menampilkan formulir edit
          $('#family-details-content').hide();
          $('#edit-family-form').show();
          
          // Mengisi formulir dengan data anggota yang dipilih
          var selectedMemberId = $('#select-family-member').val();
          var selectedMember = familyData.find(member => member.id == selectedMemberId);

          if (selectedMember) {
            $('#edit-nama-keluarga').val(selectedMember.nama_keluarga);
            $('#edit-nama').val(selectedMember.nama);
            $('#edit-tempat-lahir').val(selectedMember.tempat_lahir);
            $('#edit-tanggal-lahir').val(selectedMember.tanggal_lahir);
            $('#edit-nomor-keluarga').val(selectedMember.nomor_keluarga);
            $('#edit-hubungan-keluarga').val(selectedMember.hubungan_keluarga);
            $('#edit-member-id').val(selectedMember.id);
          }
        

        $('#edit-nama-keluarga').on('input', function() {
            this.value = this.value.toUpperCase();
          });
        });
      
        $('#edit-form').off('submit').on('submit', function(e) {
          e.preventDefault();

          var formData = $(this).serialize();
          
          $.ajax({
            url: '/edit_family',
            method: 'POST',
            data: formData,
            success: function(response) {
              alert('Data keluarga berhasil diperbarui.');
              $('#familyDetailsModal').modal('hide');
              // Tambahkan logika untuk memperbarui halaman atau tabel
            location.reload();
            },
            error: function() {
              alert('Gagal memperbarui data keluarga.');
            }
          });
        });

       $('#delete-family').off('click').on('click', function() {
          // Kosongkan dropdown sebelum diisi ulang
          $('#select-member-to-delete').empty();

          // Isi dropdown dengan anggota keluarga dari data yang dimuat
          $.each(data, function(index, member) {
            $('#select-member-to-delete').append('<option value="' + member.id + '">' + member.nama + '</option>');
          });

          // Tampilkan modal pemilihan anggota keluarga
          $('#deleteFamilyMemberModal').modal('show');
        });

        $('#confirm-delete-family-member').off('click').on('click', function() {
          var selectedMemberId = $('#select-member-to-delete').val(); // Ambil ID anggota keluarga yang dipilih

          if (selectedMemberId && confirm('Apakah Anda yakin ingin menghapus anggota keluarga ini?')) {
            $.ajax({
              url: '/delete_family_member/' + encodeURIComponent(selectedMemberId),
              method: 'DELETE',
              success: function(response) {
                alert('Anggota keluarga berhasil dihapus.');
                $('#deleteFamilyMemberModal').modal('hide'); // Tutup modal setelah penghapusan
                location.reload(); // Refresh halaman setelah penghapusan
              },
              error: function() {
                alert('Gagal menghapus anggota keluarga.');
              }
            });
          }
        });
      },
      error: function() {
        alert('Gagal memuat detail keluarga.');
      }
    });
  });

  // Menutup modal dan mengembalikan tampilan ke detail keluarga
  $('#familyDetailsModal').on('hidden.bs.modal', function () {
    $('#edit-family-form').hide(); // Menyembunyikan formulir edit
    $('#family-details-content').show(); // Menampilkan detail keluarga
  });
});

