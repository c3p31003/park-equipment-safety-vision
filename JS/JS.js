// ログインボタン
document.addEventListener("DOMContentLoaded", function () {
    const photoButton = document.getElementById("photoButton");
    const photoButtonContainer = document.getElementById("photoButtonContainer");
    const newButtonsContainer = document.getElementById("newButtonsContainer");

    photoButton.addEventListener("click", function () {
        photoButtonContainer.style.display = "none";
        newButtonsContainer.style.display = "block";
    });
});

// 点検チェックシート画面　日付入力欄
window.onload = function(){
    var getToday = new Date();
    var y = getToday.getFullYear();
    var m = getToday.getMonth() + 1;
    var d = getToday.getDate();
    var today = y + "-" + m.toString().padStart(2,'0') + "-" + d.toString().padStart(2,'0');
    document.getElementById("datepicker2").setAttribute("value",today);
    document.getElementById("datepicker2").setAttribute("min",today);
}
