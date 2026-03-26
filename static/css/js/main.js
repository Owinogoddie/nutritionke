// ── Dark / Light Theme Toggle ─────────────────────────────────────────────
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.classList.contains("dark");

  if (isDark) {
    html.classList.remove("dark");
    document.cookie = "theme=light; path=/; max-age=31536000";
  } else {
    html.classList.add("dark");
    document.cookie = "theme=dark; path=/; max-age=31536000";
  }
}

// Apply saved theme on load
(function () {
  const saved = document.cookie
    .split("; ")
    .find((row) => row.startsWith("theme="));
  if (saved && saved.split("=")[1] === "dark") {
    document.documentElement.classList.add("dark");
  }
})();

// ── Goal Selector (setup_profile) ────────────────────────────────────────
document
  .querySelectorAll('.goal-option input[type="radio"]')
  .forEach((radio) => {
    radio.addEventListener("change", function () {
      document.querySelectorAll(".goal-option div").forEach((div) => {
        div.classList.remove(
          "border-orange-500",
          "bg-orange-50",
          "dark:bg-orange-900/20",
        );
        div.classList.add("border-gray-200", "dark:border-gray-600");
      });
      if (this.checked) {
        const div = this.nextElementSibling;
        div.classList.add(
          "border-orange-500",
          "bg-orange-50",
          "dark:bg-orange-900/20",
        );
        div.classList.remove("border-gray-200", "dark:border-gray-600");
      }
    });
  });

// ── Flash message auto-dismiss ────────────────────────────────────────────
setTimeout(() => {
  document.querySelectorAll("[data-flash]").forEach((el) => {
    el.style.transition = "opacity 0.5s";
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 500);
  });
}, 4000);
