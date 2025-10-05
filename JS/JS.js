document.addEventListener("DOMContentLoaded", function () {
    const photoButton = document.getElementById("photoButton");
    const photoButtonContainer = document.getElementById("photoButtonContainer");
    const newButtonsContainer = document.getElementById("newButtonsContainer");

    photoButton.addEventListener("click", function () {
        photoButtonContainer.style.display = "none";
        newButtonsContainer.style.display = "block";
    });
});
