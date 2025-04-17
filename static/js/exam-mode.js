// Add this at the beginning of the file
console.log("Exam mode JS loaded")

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM loaded in exam mode")

    // Check if sections exist
    const sections = document.querySelectorAll(".reading-section")
    console.log(`Found ${sections.length} reading sections`)

    // Check if first section is active
    const activeSection = document.querySelector(".reading-section.active")
    console.log(`Active section: ${activeSection ? activeSection.id : "none"}`)
    // Check if we're on a test page
    const isTestPage = window.location.pathname.includes("-test/")

    if (isTestPage) {
        // Apply exam mode
        applyExamMode()

        // Add form submission handlers
        addLoadingHandlers()

        // Add navigation warning
        addNavigationWarning()
    }

    // Check if we're on the start test page
    const isStartTestPage = window.location.pathname.includes("start-test")
    if (isStartTestPage) {
        // Add loading handler for the start test form
        const startTestForm = document.getElementById("start-test-form")
        if (startTestForm) {
            startTestForm.addEventListener("submit", () => {
                showLoading("Generating your test. This may take a moment...")
            })
        }
    }
})

function applyExamMode() {
    // Add exam-mode class to body
    document.body.classList.add("exam-mode")

    // Hide header, footer, and sidebar
    const header = document.querySelector("header")
    const footer = document.querySelector("footer")
    const sidebar = document.querySelector(".dashboard-sidebar")

    if (header) header.style.display = "none"
    if (footer) footer.style.display = "none"
    if (sidebar) sidebar.style.display = "none"

    // Make main content full width
    const main = document.querySelector(".dashboard-main")
    if (main) {
        main.style.width = "100%"
        main.style.marginLeft = "0"
    }

    // Add exam mode notice
    const examNotice = document.createElement("div")
    examNotice.className = "exam-mode-notice"
    examNotice.innerHTML = `
        <div class="exam-mode-indicator">
            <span class="exam-mode-dot"></span> Exam Mode Active
        </div>
        <div class="exam-mode-actions">
            <button id="fullscreen-toggle" class="exam-mode-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8 3H5a2 2 0 0 0-2 2v3"></path>
                    <path d="M21 8V5a2 2 0 0 0-2-2h-3"></path>
                    <path d="M3 16v3a2 2 0 0 0 2 2h3"></path>
                    <path d="M16 21h3a2 2 0 0 0 2-2v-3"></path>
                </svg>
                Enter Fullscreen
            </button>
        </div>
    `
    document.body.insertBefore(examNotice, document.body.firstChild)

    // Add fullscreen toggle functionality
    const fullscreenToggle = document.getElementById("fullscreen-toggle")
    if (fullscreenToggle) {
        fullscreenToggle.addEventListener("click", toggleFullscreen)
    }

    // Create loading overlay if it doesn't exist
    if (!document.querySelector(".loading-overlay")) {
        const loadingOverlay = document.createElement("div")
        loadingOverlay.className = "loading-overlay"
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-message">Loading...</div>
            </div>
        `
        document.body.appendChild(loadingOverlay)
    }
}

function addLoadingHandlers() {
    // Add loading handlers to all forms
    const forms = document.querySelectorAll("form")
    forms.forEach((form) => {
        // Skip forms that shouldn't show loading
        if (form.classList.contains("no-loading")) return

        form.addEventListener("submit", () => {
            // Determine appropriate loading message based on form ID
            let message = "Processing..."

            if (form.id === "reading-test-form") {
                message = "Submitting your reading answers..."
            } else if (form.id === "listening-test-form") {
                message = "Submitting your listening answers..."
            } else if (form.id === "writing-test-form") {
                message = "Submitting your essays for evaluation..."
            }

            showLoading(message)
        })
    })
}

function addNavigationWarning() {
    window.addEventListener("beforeunload", (e) => {
        // Check if there are unsaved changes
        const hasUnsavedChanges = checkForUnsavedChanges()

        if (hasUnsavedChanges) {
            // Standard way of showing a confirmation dialog before leaving
            const confirmationMessage = "You have unsaved changes. Are you sure you want to leave?"
            e.returnValue = confirmationMessage
            return confirmationMessage
        }
    })
}

function checkForUnsavedChanges() {
    // Check for filled form fields that haven't been submitted
    const forms = document.querySelectorAll("form")
    let hasChanges = false

    forms.forEach((form) => {
        const inputs = form.querySelectorAll("input, textarea, select")
        inputs.forEach((input) => {
            if (input.type === "text" || input.type === "textarea") {
                if (input.value.trim() !== "") {
                    hasChanges = true
                }
            } else if (input.type === "radio" || input.type === "checkbox") {
                if (input.checked) {
                    hasChanges = true
                }
            } else if (input.type === "select-one" || input.type === "select-multiple") {
                if (input.value !== "") {
                    hasChanges = true
                }
            }
        })
    })

    return hasChanges
}

function showLoading(message = "Loading...") {
    const loadingOverlay = document.querySelector(".loading-overlay")
    const loadingMessage = document.querySelector(".loading-message")

    if (loadingMessage) {
        loadingMessage.textContent = message
    }

    if (loadingOverlay) {
        loadingOverlay.classList.add("active")
    }
}

function hideLoading() {
    const loadingOverlay = document.querySelector(".loading-overlay")
    if (loadingOverlay) {
        loadingOverlay.classList.remove("active")
    }
}

function toggleFullscreen() {
    const button = document.getElementById("fullscreen-toggle")

    if (!document.fullscreenElement) {
        // Enter fullscreen
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen()
            if (button) {
                button.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M4 14h6v6"></path>
                        <path d="M20 10h-6V4"></path>
                        <path d="M14 10l7-7"></path>
                        <path d="M3 21l7-7"></path>
                    </svg>
                    Exit Fullscreen
                `
            }
        }
    } else {
        // Exit fullscreen
        if (document.exitFullscreen) {
            document.exitFullscreen()
            if (button) {
                button.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M8 3H5a2 2 0 0 0-2 2v3"></path>
                        <path d="M21 8V5a2 2 0 0 0-2-2h-3"></path>
                        <path d="M3 16v3a2 2 0 0 0 2 2h3"></path>
                        <path d="M16 21h3a2 2 0 0 0 2-2v-3"></path>
                    </svg>
                    Enter Fullscreen
                `
            }
        }
    }
}
