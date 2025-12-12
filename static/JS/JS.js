// ログインボタン
document.addEventListener("DOMContentLoaded", function () {
  const photoButton = document.getElementById("photoButton");
  const photoButtonContainer = document.getElementById("photoButtonContainer");
  const newButtonsContainer = document.getElementById("newButtonsContainer");

  // 要素が存在する場合のみイベントを追加
  if (photoButton && photoButtonContainer && newButtonsContainer) {
    photoButton.addEventListener("click", function () {
      photoButtonContainer.style.display = "none";
      newButtonsContainer.style.display = "block";
    });
  }
});

// 点検チェックシート画面　日付入力欄
window.onload = function () {
  var getToday = new Date();
  var y = getToday.getFullYear();
  var m = getToday.getMonth() + 1;
  var d = getToday.getDate();
  var today = y + "-" + m.toString().padStart(2, '0') + "-" + d.toString().padStart(2, '0');

  // 要素が存在する場合のみ処理
  const datepicker2 = document.getElementById("datepicker2");
  if (datepicker2) {
    datepicker2.setAttribute("value", today);
    datepicker2.setAttribute("min", today);
  }
}

// ヘッダーアカウント情報（スマホ、タブレットのみ）
document.addEventListener('DOMContentLoaded', () => {
  const icon = document.getElementById('accountIcon');
  const details = document.getElementById('accountDetails');

  // 要素が存在する場合のみイベントを追加
  if (icon && details) {
    icon.addEventListener('click', () => {
      if (details.style.display === 'block') {
        details.style.display = 'none';
      } else {
        details.style.display = 'block';
      }
    });

    // 画面外クリックで閉じる
    document.addEventListener('click', (e) => {
      if (!icon.contains(e.target) && !details.contains(e.target)) {
        details.style.display = 'none';
      }
    });
  }
});
