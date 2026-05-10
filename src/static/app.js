document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const profileForm = document.getElementById("profile-form");
  const studentEmails = document.getElementById("student-emails");
  const studentsList = document.getElementById("students-list");
  const messageDiv = document.getElementById("message");

  // Function to fetch student profiles from API
  async function fetchStudents() {
    try {
      const response = await fetch("/students");
      const students = await response.json();

      studentsList.innerHTML = "";
      studentEmails.innerHTML = "";

      if (students.length === 0) {
        studentsList.innerHTML = "<p>No student profiles yet.</p>";
        return;
      }

      const list = document.createElement("ul");
      list.className = "profile-list";

      students.forEach((student) => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `
          <strong>${student.name}</strong> (${student.email})<br />
          Grade: ${student.grade_level}${student.contact_number ? ` • Contact: ${student.contact_number}` : ""}${student.enrolled_at ? ` • Enrolled: ${student.enrolled_at}` : ""}
        `;
        list.appendChild(listItem);

        const option = document.createElement("option");
        option.value = student.email;
        studentEmails.appendChild(option);
      });

      studentsList.appendChild(list);
    } catch (error) {
      studentsList.innerHTML =
        "<p>Failed to load student profiles. Please try again later.</p>";
      console.error("Error fetching students:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  function showMessage(text, type = "success") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("profile-email").value;
    const name = document.getElementById("profile-name").value;
    const grade_level = document.getElementById("profile-grade").value;
    const contact_number = document.getElementById("profile-contact").value;
    const enrolled_at = document.getElementById("profile-enrolled").value;

    const profile = {
      email,
      name,
      grade_level,
      contact_number: contact_number || undefined,
      enrolled_at: enrolled_at || undefined,
    };

    try {
      const response = await fetch("/students", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profile),
      });

      const result = await response.json();

      if (response.ok) {
        showMessage("Student profile created successfully.");
        profileForm.reset();
        fetchStudents();
      } else {
        showMessage(result.detail || "Failed to create profile.", "error");
      }
    } catch (error) {
      showMessage("Failed to create profile. Please try again.", "error");
      console.error("Error creating student profile:", error);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message);
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchStudents();
  fetchActivities();
});
