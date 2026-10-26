(function () {
  var $ = function (id) { return document.getElementById(id); };

  function calc() {
    var pages = Math.max(1, parseInt($('pages').value) || 1);
    var copies = Math.max(1, parseInt($('copies').value) || 1);
    var perPage = parseFloat($('color').value) * parseFloat($('size').value);
    var bind = parseFloat($('bind').value);

    var perCopy = pages * perPage + bind;
    var total = perCopy * copies;

    $('out').textContent = '₱' + total.toLocaleString('en-PH', { maximumFractionDigits: 0 });
    $('per').textContent = '₱' + perCopy.toLocaleString('en-PH', { maximumFractionDigits: 0 }) + ' per copy';
  }

  ['color', 'size', 'pages', 'copies', 'bind'].forEach(function (id) {
    $(id).addEventListener('input', calc);
  });

  calc();
})();
