document.addEventListener("DOMContentLoaded", () => {
  // Fetch Projects Data
  const fetchProjects = async () => {
    try {
      const response = await fetch("/FinanceManagementPortal/Project.json"); // Update with actual path or API endpoint
      if (!response.ok) throw new Error("Failed to fetch project data");
      const data = await response.json();
      console.log("Fetched Projects:", data);
      return data.projects; // Ensure your JSON structure has a "projects" array
    } catch (error) {
      console.error("Error fetching projects:", error);
      return null;
    }
  };

  // Render Projects in Table
  const renderProjects = (projects) => {
    const tableBody = document.getElementById("projects-table-body"); // Ensure this element exists
    tableBody.innerHTML = ""; // Clear any existing rows

    projects.forEach((project) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${project.project_id}</td>
        <td>${project.project_name}</td>
        <td>${project.project_budget.toFixed(2)}</td>
        <td>${project.start_date || "N/A"}</td>
        <td>${
          project.end_date === "0000-00-00" || !project.end_date
            ? "N/A"
            : project.end_date
        }</td>
        <td>${project.notes}</td>
        <td>${project.status}</td>
      `;
      tableBody.appendChild(row);
    });
  };

  // Initialize Page
  (async () => {
    const projects = await fetchProjects();
    if (projects) renderProjects(projects);
  })();

  // Bulk Upload
  document.getElementById("upload-button").addEventListener("click", () => {
    const fileInput = document.getElementById("bulk-upload");
    const file = fileInput.files[0];

    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    // Validate file type
    if (!file.name.endsWith(".csv")) {
      alert("Please upload a valid CSV file.");
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      alert("File size exceeds the 5MB limit.");
      return;
    }

    const formData = new FormData();
    formData.append("bulk_file", file);

    // Show loader
    showLoader(true);

    fetch("./Deployment.html", {
      // Update with the correct PHP file path
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide loader
        showLoader(false);

        if (data.status === "success") {
          alert(data.message);
          location.reload(); // Reload to fetch updated data
        } else {
          alert(data.message);
        }
      })
      .catch((error) => {
        // Hide loader
        showLoader(false);

        console.error("Error uploading file:", error);
        alert("An error occurred while uploading the file. Please try again.");
      });
  });

  // Form Submission
  setupFormSubmission();

  // Function to show or hide loader
  function showLoader(show) {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = show ? "block" : "none";
  }

  // Function to set up form submission
  function setupFormSubmission() {
    const form = document.getElementById("transactionForm");
    if (!form) return;

    form.addEventListener("submit", (event) => {
      event.preventDefault(); // Prevent the default form submission behavior

      const formData = new FormData(form);

      // Show loader
      showLoader(true);

      fetch("", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          // Hide loader
          showLoader(false);

          const messageBox = document.getElementById("messageBox");
          if (messageBox) {
            messageBox.style.display = "block";
            if (data.status === "success") {
              messageBox.style.backgroundColor = "#d4edda";
              messageBox.style.color = "#155724";
              messageBox.textContent = data.message;

              // Clear the form fields after a successful submission
              form.reset();

              // Hide the modal and overlay
              const modal = document.getElementById("addTransactionModal");
              const overlay = document.getElementById("overlay");
              if (modal) modal.style.display = "none";
              if (overlay) overlay.style.display = "none";
            } else {
              messageBox.style.backgroundColor = "#f8d7da";
              messageBox.style.color = "#721c24";
              messageBox.textContent = data.message;
            }

            // Hide the message box after a few seconds
            setTimeout(() => {
              messageBox.style.display = "none";
            }, 15000);
          }
        })
        .catch((error) => {
          // Hide loader
          showLoader(false);

          console.error("Error:", error);
          alert(
            "An error occurred while submitting the form. Please try again."
          );
        });
    });
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
});
