/**
 * CampusConnect - Main JavaScript (Simplified)
 */

"use strict";

document.addEventListener("DOMContentLoaded", function () {

  // ── Delete Confirmation ──────────────────────────────────────
  document.querySelectorAll("[data-confirm]").forEach(el => {
    el.addEventListener("click", function (e) {
      const message = this.getAttribute("data-confirm") ||
                      "Are you sure? This action cannot be undone.";
      if (!confirm(message)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });

  // ── Tooltip initialization ───────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

});
