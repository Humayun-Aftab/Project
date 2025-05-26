document.addEventListener("DOMContentLoaded", () => {


  // Function to show or hide loader
  function showLoader(show) {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = show ? "block" : "none";
  }


  // Update Form
  function initializeUpdateForm() {
    const form = document.getElementById("updateTransactionForm");
    if (!form) return;

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const url = form.getAttribute("action")

      const formData = new FormData(form);

      // Show loader
      showLoader(true);

      fetch(url, {
        method: "PATCH",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Hide loader
          showLoader(false);
          showMessage(data, form)
        })
        .catch((error) => {
          // Hide loader
          showLoader(false);
          console.error("Error:", error);
          alert(
            "An error occurred while submitting the form. Please try again."
          );
        }).finally(() => {
          // Hide the modal and overlay
          const modal = document.getElementById("updateTransactionModal");
          const overlay = document.getElementById("overlay");
          if (modal) modal.classList.remove("active")
          if (overlay) overlay.style.display = "none";
        })
    });
  }


  // Delete Form
  function initializeDeleteForm() {
    const form = document.getElementById("deleteTransactionForm");
    if (!form) return;

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const url = form.getAttribute("action")

      const params = new URLSearchParams(new FormData(form));

      // Show loader
      showLoader(true);

      fetch(url+"?"+params, {
        method: "DELETE"
      })
        .then((response) => response.json())
        .then((data) => {
          // Hide loader
          showLoader(false);
          showMessage(data, form)
        })
        .catch((error) => {
          // Hide loader
          showLoader(false);
          console.error("Error:", error);
          alert(
            "An error occurred while submitting the form. Please try again."
          );
        }).finally(() => {
          // Hide the modal and overlay
          const modal = document.getElementById("deleteTransactionModal");
          const overlay = document.getElementById("overlay");
          if (modal) modal.classList.remove("active")
          if (overlay) overlay.style.display = "none";
        })
    });
  }


  // Auto-fill form fields
  document.getElementById("fillTransaction")
    .addEventListener("click", fillUpdateForm)
  function fillUpdateForm() {
    let requiredId = document.getElementById("id").value
    let t = window.transactions.find(v => v.id == requiredId) 
    const form = document.getElementById("updateTransactionForm");

    for (const [key, value] of Object.entries(t)) {
      const input = form.elements.namedItem(key);
      if (input) {
        input.value = value;
      }
    }
  }


  // Function to set up form submission
  function setupFormSubmission() {
    const form = document.getElementById("transactionForm");
    if (!form) return;

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const url = form.getAttribute("action")

      const formData = new FormData(form);

      // Show loader
      showLoader(true);

      fetch(url, {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Hide loader
          showLoader(false);
          showMessage(data, form)
        })
        .catch((error) => {
          // Hide loader
          showLoader(false);
          console.error("Error:", error);
          alert(
            "An error occurred while submitting the form. Please try again."
          );
        }).finally(() => {
          // Hide the modal and overlay
          const modal = document.getElementById("addTransactionModal");
          const overlay = document.getElementById("overlay");
          if (modal) modal.classList.remove("active")
          if (overlay) overlay.style.display = "none";
        })
    });
  }



  document.getElementById("searchForm").addEventListener("submit", handleSearch)
  function handleSearch(event) {
    event.preventDefault();
    const form = event.target
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);
    const url = form.getAttribute("action")

    // Show loader
    showLoader(true);

    fetch(`${url}?${params}`) 
      .then((response) => response.json())
      .then(json => {
        renderTransactions(json.transactions)
      })
  }

  // Export Data
  window.exportData = function (format) {
    // Get table data
    const table = document.getElementById("transactionTable");
    const rows = Array.from(table.querySelectorAll("tr")).map((tr) =>
      Array.from(tr.querySelectorAll("th, td")).map((td) => td.innerText)
    );

    try {
      if (format === "pdf") {
        // PDF Export using jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        doc.autoTable({
          head: [rows[0]], // Header row
          body: rows.slice(1), // Data rows
        });

        doc.save("transactions.pdf");
        alert("PDF file generated successfully!");
      } else if (format === "excel") {
        // Excel Export using SheetJS
        const workbook = XLSX.utils.book_new();
        const worksheet = XLSX.utils.aoa_to_sheet(rows);
        XLSX.utils.book_append_sheet(workbook, worksheet, "Transactions");
        XLSX.writeFile(workbook, "transactions.xlsx");
        alert("Excel file generated successfully!");
      } else {
        console.error("Unsupported format:", format);
      }
    } catch (error) {
      console.error("Export error:", error);
      alert("An error occurred while exporting data. Please try again.");
    }
  };

  (async () => {
    setupFormSubmission();
    initializeUpdateForm();
    initializeDeleteForm();
    window.exportData = exportData;
  })();
});


const showMessage = (data, form) => {
  const messageBox = document.getElementById("messageBox");
  if (messageBox) {
    messageBox.style.display = "block";

    if (data.status === "success") {
      messageBox.style.backgroundColor = "#d4edda";
      messageBox.style.color = "#155724";
      messageBox.textContent = data.text;

      // Clear the form fields after a successful submission
      form.reset();

    } else {
      messageBox.style.backgroundColor = "#f8d7da";
      messageBox.style.color = "#721c24";
      messageBox.textContent = data.text;
    }

    // Hide the message box after a few seconds
    setTimeout(() => {
      messageBox.style.display = "none";
    }, 10000);
  }
}


const renderTransactions = (transactions) => {
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

