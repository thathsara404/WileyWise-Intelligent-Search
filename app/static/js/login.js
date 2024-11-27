document.addEventListener("DOMContentLoaded", async () => {
    const title = document.querySelector(".rotating-title");
    const letters = [...title.textContent.trim()];
    title.innerHTML = letters
        .map((letter) => (letter === " " ? "&nbsp;" : `<span>${letter}</span>`))
        .join("");
});