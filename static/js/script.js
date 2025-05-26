document.addEventListener("DOMContentLoaded", async () => {
  await initApp();
  mobileMenu();
  highlightActiveNav();
  initializeDarkMode();
  setupDropdown();
  setupModal();
  setupSectionToggle();
});

function mobileMenu() {
  const openButton = document.getElementById("open-sidebar-button");
  const navbar = document.getElementById("navbar");
  const closed = document.getElementById("close-sidebar-button");

  if (openButton && navbar && closed) {
    openButton.addEventListener("click", () => {
      navbar.classList.add("show");
    });

    closed.addEventListener("click", () => {
      navbar.classList.remove("show");
    });
  } else {
    console.warn("Sidebar menu elements are missing on this page.");
  }
}

// Initialize the application by loading header and sidebar components
const initApp = async () => {
  try {
    const headerResponse = await fetch("/static/components/header.html");
    if (!headerResponse.ok) throw new Error("Failed to load header");
    const headerData = await headerResponse.text();
    document.querySelector(".header--wrapper").innerHTML = headerData;

  } catch (error) {
    console.error("Error loading components:", error);
  }
};

// Function to highlight the active navigation link
function highlightActiveNav() {
  const activePage = window.location.pathname;
  document.querySelectorAll("nav a").forEach((link) => {
    if (link.href.includes(`${activePage}`)) {
      link.classList.add("active");
    }
  });
}

// Initialize dark mode toggle functionality
function initializeDarkMode() {
  const themeSwitch = document.getElementById("theme-switch");
  if (!themeSwitch) return;

  const enableDarkMode = () => {
    document.body.classList.add("darkmode");
    localStorage.setItem("darkmode", "active");
  };
  const disableDarkMode = () => {
    document.body.classList.remove("darkmode");
    localStorage.setItem("darkmode", "inactive");
  };

  if (localStorage.getItem("darkmode") === "active") enableDarkMode();

  themeSwitch.addEventListener("click", () => {
    localStorage.getItem("darkmode") === "active"
      ? disableDarkMode()
      : enableDarkMode();
  });
}

// Setup dropdown menu toggle
function setupDropdown() {
  const dropdownBtn = document.querySelector(".dropdown-btn");
  if (!dropdownBtn) return;

  const overlay1 = document.getElementById("overlay1");
  dropdownBtn.addEventListener("click", () => {
    document.querySelector(".dropdown-content").classList.toggle("show");
    if (overlay1) overlay1.style.display = "block";
  });
}

// Setup modal functionality for "Add Transaction"
function setupModal() {
  const overlay = document.getElementById("overlay");
  const addTransactionBtn = document.getElementById("addTransactionBtn");
  const addTransactionModal = document.getElementById("addTransactionModal");

  const updateTransactionBtn = document.getElementById("updateTransactionBtn");
  const updateTransactionModal = document.getElementById("updateTransactionModal");

  const deleteTransactionBtn = document.getElementById("deleteTransactionBtn")
  const deleteTransactionModal = document.getElementById("deleteTransactionModal")

  if (!overlay || !addTransactionBtn || !addTransactionModal) return;

  addTransactionBtn.addEventListener("click", () => {
    addTransactionModal.classList.add("active");
    overlay.style.display = "block";
  });
  updateTransactionBtn.addEventListener("click", () => {
    updateTransactionModal.classList.add("active");
    overlay.style.display = "block";
  });
  deleteTransactionBtn.addEventListener("click", () => {
    deleteTransactionModal.classList.add("active")
    overlay.style.display = "block"
  })

  overlay.addEventListener("click", () => {
    addTransactionModal.classList.remove("active");
    updateTransactionModal.classList.remove("active");
    deleteTransactionModal.classList.remove("active")
    overlay.style.display = "none";
  });
}

// Setup section toggle for switching between sections
function setupSectionToggle() {
  const toggleButtons = document.querySelectorAll(".toggle-btn");
  const sections = document.querySelectorAll(".section");
  if (!toggleButtons.length || !sections.length) return;

  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      toggleButtons.forEach((btn) => btn.classList.remove("active"));
      sections.forEach((section) => section.classList.remove("active"));

      button.classList.add("active");
      const sectionId = button.getAttribute("data-section");
      document.getElementById(sectionId).classList.add("active");
    });
  });
}

const fetchTransactions = async () => {
  try {
    const response = await fetch("/api/transaction"); // Update the path
    if (!response.ok) throw new Error("Failed to fetch transaction data");
    const data = await response.json();
    return data.transactions; // Ensure your JSON structure has a "transactions" array
  } catch (error) {
    console.error("Error fetching transactions:", error);
    return null;
  }
};

const renderTransactions = (transactions) => {
  window.transactions = transactions
  const tableBody = document.getElementById("transactions-table-body"); // Ensure this element exists
  tableBody.innerHTML = ""; // Clear existing rows

  transactions.forEach((transaction) => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${transaction.id}</td>
        <td>${transaction.amount}</td>
        <td>${transaction.type}</td>
        <td>${transaction.date}</td>
        <td>${transaction.notes}</td>
        <td>${transaction.category}</td>
      `;
    tableBody.appendChild(row);
  });
};


(async () => {
  const transactions = await fetchTransactions();
  if (transactions) renderTransactions(transactions);
})();