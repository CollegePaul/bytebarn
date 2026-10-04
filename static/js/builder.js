/* ByteBarn PC Builder
   --------------------
   Adds up the parts as you choose them, and tells you how far over or under
   budget you are.

   Everything here runs in the browser. The server never sees these numbers. */

(function () {
  "use strict";

  // The currency symbol is set by Django in the <script> tag, so we do not have
  // to change it in two places if the shop starts using dollars.
  var script = document.currentScript;
  var CURRENCY = script ? script.dataset.currency || "£" : "£";

  var selects = document.querySelectorAll("[data-part-select]");
  var totalEl = document.getElementById("build-total");
  var countEl = document.getElementById("build-count");
  var budgetEl = document.getElementById("budget");
  var budgetMsgEl = document.getElementById("budget-message");
  var addButton = document.getElementById("add-build");
  var resetButton = document.getElementById("reset-build");

  if (!selects.length) {
    return; // No products in the shop yet, nothing to wire up.
  }

  // 1234.5 -> "£1,234.50"
  function money(amount) {
    return CURRENCY + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  function chosenParts() {
    return Array.prototype.filter
      .call(selects, function (select) {
        return select.value !== "";
      })
      .map(function (select) {
        var option = select.options[select.selectedIndex];
        return {
          select: select,
          price: parseFloat(option.dataset.price) || 0
        };
      });
  }

  function recalculate() {
    var parts = chosenParts();

    var total = parts.reduce(function (running, part) {
      return running + part.price;
    }, 0);

    // --- the big number ---
    totalEl.textContent = money(total);

    // --- how many slots are filled ---
    if (parts.length === 0) {
      countEl.textContent = "No parts chosen yet";
    } else if (parts.length === 1) {
      countEl.textContent = "1 part chosen";
    } else {
      countEl.textContent = parts.length + " parts chosen";
    }

    // --- the basket button ---
    addButton.disabled = parts.length === 0;

    // --- the budget line ---
    var budget = parseFloat(budgetEl.value);
    budgetMsgEl.className = "small text-body-secondary";

    if (!isNaN(budget) && budget > 0) {
      if (total > budget) {
        budgetMsgEl.className = "small budget-over fw-semibold";
        budgetMsgEl.textContent = money(total - budget) + " over budget.";
      } else {
        budgetMsgEl.className = "small budget-ok fw-semibold";
        budgetMsgEl.textContent =
          money(budget - total) + " left to spend" +
          (total > 0 ? " — enough to add " + money(Math.min(budget - total, 500)) + " more." : ".");
      }
    } else if (total > 0) {
      budgetMsgEl.textContent = "Set a budget to see how much room is left.";
    }
  }

  selects.forEach(function (select) {
    select.addEventListener("change", recalculate);
  });

  budgetEl.addEventListener("input", recalculate);

  resetButton.addEventListener("click", function () {
    selects.forEach(function (select) {
      select.value = "";
    });
    budgetEl.value = "";
    recalculate();
  });

  // Run once on page load so the page never shows a blank total.
  recalculate();
})();