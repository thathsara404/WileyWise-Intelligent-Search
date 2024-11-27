let savedConversations = []; // Array to store saved conversations

async function askQuestion() {
    const query = document.getElementById("query").value;
    const strictness = document.getElementById("strictness").value;
    const spinner = document.getElementById("loadingSpinner");

    if (query && strictness) {
        // Show the spinner
        spinner.classList.remove("d-none");
        clearSections();
    }

    // Fetch the answer and quiz
    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, strictness }),
    });

    const data = await response.json();

    if (data) {
        // Hide the spinner after the response is processed
        spinner.classList.add("d-none");
    }

    const generatedSection = document.getElementById("generated");
    generatedSection.classList.remove("hidden");
    generatedSection.classList.add("fade-in");

    // Display the answer
    document.getElementById("answer").innerText = data.answer || data.error;

    // Display the link if available
    const articleLink = document.getElementById("article-link");
    if (data.link && data.link !== "No link available") {
        articleLink.href = data.link;
        articleLink.classList.remove("hidden");
    } else {
        articleLink.classList.add("hidden");
    }

    // Parse and render the quiz
    if (data.quiz) {
        const quizData = JSON.parse(data.quiz.replace(/'/g, '"')); // Replace single quotes with double quotes for valid JSON
        renderQuiz(quizData);
    }
}

function renderQuiz(quizData) {
    const quizContainer = document.getElementById("quiz");
    quizContainer.innerHTML = ""; // Clear existing content

    quizData.questions.forEach((q, index) => {
        const questionDiv = document.createElement("div");
        questionDiv.className = "question mb-4 p-3 border rounded bg-light";

        // Add the question text
        const questionText = document.createElement("p");
        questionText.textContent = `${index + 1}. ${q.question}`;
        questionText.className = "fw-bold";
        questionDiv.appendChild(questionText);

        // Render True/False questions
        if (q.type === "True/False") {
            ["True", "False"].forEach((option) => {
                const button = document.createElement("button");
                button.textContent = option;
                button.className = "btn btn-primary text-white me-2 mb-2";
                button.setAttribute("data-correct-answer", q.correct_answer);
                button.onclick = () => checkAnswer(q.correct_answer, option, button, questionDiv);
                questionDiv.appendChild(button);
            });
        } else if (q.type === "Multiple Choice") {
            // Render Multiple-Choice questions
            q.options.forEach((option) => {
                const button = document.createElement("button");
                button.textContent = option;
                button.className = "btn btn-primary text-white me-2 mb-2";
                button.setAttribute("data-correct-answer", q.correct_answer);
                button.onclick = () => checkAnswer(q.correct_answer, option, button, questionDiv);
                questionDiv.appendChild(button);
            });
        } else if (q.type === "Fill in the Blank") {
            // Render Fill-in-the-Blank questions
            const inputGroup = document.createElement("div");
            inputGroup.className = "input-group mb-3";

            const inputBox = document.createElement("input");
            inputBox.type = "text";
            inputBox.placeholder = "Your answer here";
            inputBox.className = "form-control";
            inputGroup.appendChild(inputBox);

            const submitButton = document.createElement("button");
            submitButton.textContent = "Submit";
            submitButton.className = "btn btn-primary text-white";
            submitButton.setAttribute("data-correct-answer", q.correct_answer);
            submitButton.onclick = () => {
                const userAnswer = inputBox.value.trim();
                checkAnswer(q.correct_answer, userAnswer, inputBox, questionDiv);
            };
            inputGroup.appendChild(submitButton);

            questionDiv.appendChild(inputGroup);
        }

        quizContainer.appendChild(questionDiv);
    });

    // Add the Retry Button
    const retryButton = document.createElement("button");
    retryButton.textContent = "Retry Quiz";
    retryButton.className = "btn btn-secondary mt-4 retry-button";
    retryButton.onclick = resetQuiz;
    quizContainer.appendChild(retryButton);
}

function resetQuiz() {
    const quizContainer = document.getElementById("quiz");

    // Reset all buttons
    const buttons = quizContainer.querySelectorAll("button");
    buttons.forEach((button) => {
        button.disabled = false;
        button.style.backgroundColor = ""; // Clear background color
        button.style.color = ""; // Reset text color
    });

    // Clear input fields
    const inputs = quizContainer.querySelectorAll("input");
    inputs.forEach((input) => {
        input.value = ""; // Clear input value
        input.style.backgroundColor = ""; // Reset input background color
        input.style.color = ""; // Reset input text color if needed
    });

    // Re-enable submit buttons for Fill-in-the-Blank questions
    const inputGroups = quizContainer.querySelectorAll(".input-group button");
    inputGroups.forEach((button) => {
        button.disabled = false;
    });
}

function checkAnswer(correctAnswer, userAnswer, element, questionDiv) {
    const modalTitle = document.getElementById("feedbackModalLabel");
    const modalBody = document.getElementById("feedbackModalBody");

    const isCorrect = userAnswer.toLowerCase() === correctAnswer.toLowerCase();

    // Provide visual feedback
    if (isCorrect) {
        element.style.backgroundColor = "green";
        element.style.color = "white";
        modalTitle.textContent = "Correct!";
        modalBody.innerHTML = `<p>Your answer is correct! Great job.</p>`;
    } else {
        element.style.backgroundColor = "red";
        element.style.color = "white";
        modalTitle.textContent = "Incorrect!";
        modalBody.innerHTML = `<p>Oops! The correct answer is: <strong>${correctAnswer}</strong>.</p>`;
    }

    // Disable only the buttons related to the current question
    const relatedButtons = questionDiv.querySelectorAll("button:not(.retry-button)");
    relatedButtons.forEach((btn) => {
        btn.disabled = true;
    });

    const feedbackModal = new bootstrap.Modal(document.getElementById("feedbackModal"));
    feedbackModal.show();
}

async function saveConversation() {
    const query = document.getElementById("query").value;
    const answer = document.getElementById("answer").innerText;
    const quiz = document.getElementById("quiz").innerHTML;
    const strictness = document.getElementById("strictness").value;
    const articleLink = document.getElementById("article-link").href;

    if (!query || !answer) {
        showErrorModal("Error", "Please generate an answer before saving!");
        return;
    }

    const response = await fetch("/save_conversation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, answer, quiz, strictness, link: articleLink }),
    });

    const result = await response.json();
    if (response.ok) {
        await loadSavedConversations(); // Reload the saved conversations
    } else {
        showErrorModal("Error", result.error || "Failed to save conversation");
    }
}

async function loadSavedConversations() {
    const response = await fetch("/get_saved_conversations");
    const savedConversations = await response.json();

    if (response.ok) {
        const savedList = document.getElementById("saved-conversations");
        savedList.innerHTML = ""; // Clear the existing list

        savedConversations.forEach((conversation) => {
            const listItem = document.createElement("li");
            listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

            // Container for label and text
            const textContainer = document.createElement("div");
            textContainer.classList.add("d-flex", "flex-column");

            // Strictness label
            const strictnessLabel = document.createElement("span");
            strictnessLabel.textContent = conversation.strictness;
            strictnessLabel.classList.add("badge", "bg-secondary", "mb-1");
            strictnessLabel.style.display = "inline-block";
            strictnessLabel.style.whiteSpace = "nowrap"; // Prevent wrapping
            strictnessLabel.style.width = "max-content"; // Match width to text
            strictnessLabel.style.padding = "0.25em 0.5em"; // Ensure consistent spacing
            textContainer.appendChild(strictnessLabel);

            // Query text
            const queryText = document.createElement("span");
            queryText.textContent = conversation.query;
            textContainer.appendChild(queryText);

            // Append the text container to the list item
            listItem.appendChild(textContainer);

            // Delete button
            const deleteButton = document.createElement("button");
            deleteButton.classList.add("btn", "btn-danger", "btn-sm");
            deleteButton.innerHTML = `<i class="bi bi-trash"></i>`;
            deleteButton.onclick = (e) => {
                e.stopPropagation(); // Prevent triggering the loadConversation event
                deleteConversation(conversation.query, conversation.strictness);
            };

            // Append the delete button to the list item
            listItem.appendChild(deleteButton);

            // Attach click event to load the saved conversation
            listItem.addEventListener("click", () => {
                loadConversation(conversation); // Pass the full conversation object
            });

            savedList.appendChild(listItem);
        });
    } else {
        showErrorModal("Error", savedConversations.error || "Failed to load conversations");
    }
}


async function deleteConversation(query, strictness) {
    // Send a delete request to the backend
    const response = await fetch("/delete_conversation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, strictness }), // Send the query and strictness to identify the conversation
    });

    const result = await response.json();
    if (response.ok) {
        await loadSavedConversations(); // Reload the list from the backend after deletion
    } else {
        showErrorModal("Error", result.error || "Failed to delete conversation");
    }
}


function showErrorModal(title, message) {
    const modalTitle = document.getElementById("errorModalTitle");
    const modalBody = document.getElementById("errorModalBody");

    modalTitle.textContent = title;
    modalBody.textContent = message;

    const errorModal = new bootstrap.Modal(document.getElementById("errorModal"));
    errorModal.show();
}

function updateSavedConversations() {
    const savedList = document.getElementById("saved-conversations");
    savedList.innerHTML = ""; // Clear the existing list

    savedConversations.forEach((item, index) => {
        const listItem = document.createElement("li");
        listItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");

        // Add the query and strictness as the list item's text
        const listItemText = document.createElement("span");
        listItemText.textContent = `${item.query} - ${item.strictness}`;
        listItem.appendChild(listItemText);

        // Add a delete button with a bin icon
        const deleteButton = document.createElement("button");
        deleteButton.classList.add("btn", "btn-danger", "btn-sm");
        deleteButton.innerHTML = `<i class="bi bi-trash"></i>`; // Bootstrap bin icon
        deleteButton.onclick = () => deleteConversation(index);
        listItem.appendChild(deleteButton);

        // Add a click event to load the saved conversation
        listItemText.addEventListener("click", () => {
            loadConversation(index);
        });

        savedList.appendChild(listItem);
    });
}

document.addEventListener("DOMContentLoaded", async () => {
    const title = document.querySelector(".rotating-title");
    const letters = [...title.textContent.trim()];
    title.innerHTML = letters
        .map((letter) => (letter === " " ? "&nbsp;" : `<span>${letter}</span>`))
        .join("");

    await loadSavedConversations(); // Load saved conversations
    await loadUserData(); // Load user data
});

async function loadUserData() {
    const userDataReq = await fetch("/get_user_details");
    const userData = await userDataReq.json();
    if (userData) {
        document.getElementById("username").innerHTML = userData.username;
    }
}

function loadConversation(conversation) {
    // Update the query input field
    document.getElementById("query").value = conversation.query;

    // Update the answer section
    document.getElementById("answer").innerText = conversation.answer;

    // Update the strictness dropdown
    const strictnessDropdown = document.getElementById("strictness");
    strictnessDropdown.value = conversation.strictness;

    // Parse and render the quiz data
    const quizContainer = document.getElementById("quiz");
    quizContainer.innerHTML = conversation.quiz;

    // Update the article link
    const articleLink = document.getElementById("article-link");
    if (conversation.link && conversation.link !== "No link available") {
        articleLink.href = conversation.link;
        articleLink.classList.remove("hidden");
    } else {
        articleLink.classList.add("hidden");
    }

    // Reinitialize button functionality for True/False and Multiple Choice questions
    const questionDivs = quizContainer.querySelectorAll(".question");
    questionDivs.forEach((questionDiv) => {
        const buttons = questionDiv.querySelectorAll("button:not(.retry-button)");
        buttons.forEach((button) => {
            const correctAnswer = button.getAttribute("data-correct-answer");
            const userAnswer = button.textContent.trim();

            if (correctAnswer) {
                button.onclick = () => checkAnswer(correctAnswer, userAnswer, button, questionDiv);
            }
        });

        // Reinitialize Submit buttons for Fill-in-the-Blank questions
        const inputGroupButton = questionDiv.querySelector(".input-group button");
        const inputField = questionDiv.querySelector(".input-group input");

        if (inputGroupButton && inputField) {
            const correctAnswer = inputGroupButton.getAttribute("data-correct-answer");
            inputGroupButton.onclick = () => {
                const userAnswer = inputField.value.trim();
                checkAnswer(correctAnswer, userAnswer, inputField, questionDiv);
            };
        }
    });

    // Remove any existing Retry Quiz button
    const existingRetryButton = quizContainer.querySelector(".retry-button");
    if (existingRetryButton) {
        existingRetryButton.remove();
    }

    // Add a Retry Quiz button
    const retryButton = document.createElement("button");
    retryButton.textContent = "Retry Quiz";
    retryButton.className = "btn btn-secondary mt-4 retry-button";
    retryButton.onclick = resetQuiz; // Link to the resetQuiz function
    quizContainer.appendChild(retryButton);

    const generatedSection = document.getElementById("generated");
    generatedSection.classList.remove("hidden");
    generatedSection.classList.add("fade-in");
}

function clearSections() {
    document.getElementById("answer").innerHTML = "";
    document.getElementById("quiz").innerHTML = "";
    const generatedSection = document.getElementById("generated");
    generatedSection.classList.add("hidden");
}
