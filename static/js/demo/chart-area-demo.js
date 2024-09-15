// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito, -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Fungsi untuk memformat angka
function number_format(number, decimals, dec_point, thousands_sep) {
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

// Fungsi inisialisasi chart keluarga
function initFamilyChart(data) {
  // Data untuk chart pertama (Keluarga)
  var familyData = {
    labels: ["Kepala Keluarga", "Istri", "Anak"],
    datasets: [{
      label: '&nbsp;Jumlah',
      data: [data.kepala_keluarga, data.istri, data.anak],
      backgroundColor: ['#FF6384', '#FFCE56', '#6FFFE9'],
      hoverBackgroundColor: ['#FF6384', '#FFCE56', '#6FFFE9'],
      borderWidth: 2,
      borderColor: '#ffffff',
      hoverBorderColor: '#000000',
      hoverOffset: 15,
      borderRadius: 5
    }]
  };

  // Opsi chart
  var chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
        position: 'bottom',
        labels: {
          color: '#FFFFFF',
          font: {
            family: 'Arial, sans-serif',
            size: 14,
            weight: 'bold'
          },
          usePointStyle: true,
          padding: 20
        }
      },
      title: {
        display: true,
        color: '#6FFFE9',
        font: {
          family: 'Arial, sans-serif',
          size: 20,
          weight: 'bold'
        },
        padding: 20
      },
      tooltip: {
        enabled: true,
        backgroundColor: '#000000',
        titleColor: '#FFFFFF',
        bodyFont: {
          size: 14
        },
        callbacks: {
          label: function(tooltipItem) {
            return tooltipItem.label + ': ' + number_format(tooltipItem.raw, 0, ',', '.') + ' orang';
          },
          title: function() {
            return '';
          }
        }
      }
    },
    animation: {
      animateScale: true,
      animateRotate: true,
    }
  };

  // Inisialisasi chart pertama (Pie Chart untuk Keluarga)
  var ctxLeft = document.getElementById('familyPieChartLeft').getContext('2d');
  new Chart(ctxLeft, {
    type: 'pie',
    data: familyData,
    options: chartOptions
  });
}

// Fungsi untuk menampilkan data 'Products Sold' di progress bar
function initProductSold(data) {
  const container = document.getElementById('productsSold');
  container.innerHTML = '';

  data.forEach(item => {
    const percentage = (item.total / 800) * 100;
    const progressBarColor = item.jenissurat === 'Oblong T-Shirt' ? 'bg-warning' : 'bg-success';
const progressElement = `
  <div class="mb-3">
    <div class="medium text-gray-500">${item.jenissurat}
      <div class="medium float-right"><b>${number_format(item.total)}</b></div>
    </div>
    <div class="progress" style="height: 12px;">
      <div class="progress-bar ${progressBarColor}" role="progressbar" style="width: ${percentage}%" aria-valuenow="${percentage}" aria-valuemin="0" aria-valuemax="100"></div>
    </div>
  </div>
`;


    container.innerHTML += progressElement;
  });
}

// Mengambil data dan inisialisasi chart serta progress bar
document.addEventListener('DOMContentLoaded', function() {
  // Fetch data untuk chart keluarga
  fetch('/api/family-stats')
    .then(response => response.json())
    .then(data => {
      initFamilyChart(data);
    })
    .catch(error => console.error('Error fetching family data:', error));

  // Fetch data untuk progress bar 'Products Sold'
  fetch('/api/product_sold_data')
    .then(response => response.json())
    .then(data => {
      initProductSold(data);
    })
    .catch(error => console.error('Error fetching product sold data:', error));
});
