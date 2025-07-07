// Script for index.html

// Document Listeners
document.addEventListener("DOMContentLoaded", function () {
    // cache common DOM elements
    const sprintSelect = document.querySelector("select[name='sprint']");
    const autoMode = document.getElementById("auto_mode");
    const autoTaskDiv = document.getElementById("auto-task-select");
    const taskChecklist = document.getElementById("task-checklist");
    const manualFields = document.getElementById("manual-entry-fields");
    const extraTaskButtonWrapper = document.getElementById("extra-task-button-wrapper");
    const manualAddBtn = document.getElementById("manual-add-btn");
    const autoLoading = document.getElementById("auto-loading");

    // Initialize all primary selects with the correct hidden fields visibility
    document.querySelectorAll(".primary-select").forEach(select => {
        toggleSecondaryType(select);
    });

    // toggle UI based on wheather auto mode is selected
    function toggleEntryMode(isAuto) {
        autoTaskDiv.style.display = isAuto ? "block" : "none";
        manualFields.style.display = isAuto ? "none" : "block";
        manualAddBtn.style.display = isAuto ? "none" : "block";
        extraTaskButtonWrapper.style.display = isAuto ? "block" : "none";
    }

    // Load tasks for the selected sprint
    function loadTasksForSprint(sprintId) {
        if (!sprintId) return;
        fetch(`/get_tasks?sprint_id=${sprintId}`)
            .then(res => res.json())
            .then(tasks => {
                taskChecklist.innerHTML = "";
                if (!tasks.length) {
                    taskChecklist.innerHTML = "<li>No tasks found for this sprint.</li>";
                    return;
                }
                tasks.forEach(task => {
                    const item = document.createElement("li");
                    item.innerHTML = `
                        <label>
                            <input type="checkbox" name="selected_tasks" value="${task.id}" checked>
                            ${task.name}
                        </label>`;
                    taskChecklist.appendChild(item);
                });
            })
            .catch(err => {
                console.error("Error loading tasks:", err);
                taskChecklist.innerHTML = "<li>Error loading tasks. Check console.</li>";
            })
            .finally(() => {
                autoLoading.style.display = "none";
            });
    }

    // Toggle visibility based on entry mode
    document.querySelectorAll("input[name='entry_mode']").forEach(radio => {
        radio.addEventListener("change", function () {
            const isAuto = autoMode.checked;
            toggleEntryMode(isAuto);

            if (isAuto && sprintSelect.value) {
                autoLoading.style.display = "flex";
                loadTasksForSprint(sprintSelect.value);
            }
        });
    });

    // If sprint is changed while in auto mode, load tasks
    sprintSelect.addEventListener("change", function () {
        if (autoMode.checked) {
            autoLoading.style.display = "flex";
            loadTasksForSprint(this.value);
        }
    });
    // initial state check on page load
    const isAutoInit = autoMode.checked;
    toggleEntryMode(isAutoInit)
    if (isAutoInit && sprintSelect.value) {
        loadTasksForSprint(sprintSelect.value);
    }
});

// Helper functions

// Add entry for manual task input mode
function addEntry() {
    const block = document.createElement('div');
    block.className = 'entry-block';
    block.innerHTML = `
        <label for="type">Tag</label>
        <button type="button" class="button-secondary" onclick="this.parentElement.remove()" style="float: right;">Remove Entry</button>
        <select name="type" class="input-select primary-select" onchange="toggleSecondaryType(this)">
            <option value="Feature">Feature</option>
            <option value="Bug">Bug</option>
            <option value="Enhancement">Enhancement</option>
            <option value="DevOps">DevOps</option>
            <option value="Combination">Combination</option>
        </select>

        <label class="type-hidden-label" style="display: none;">Specify Your Combination of Tags</label>
        <select name="type-hidden-1" class="input-select-hidden secondary-select">
            <option value="Feature">Feature</option>
            <option value="Bug">Bug</option>
            <option value="Enhancement">Enhancement</option>
            <option value="DevOps">DevOps</option>
        </select>

        <select name="type-hidden-2" class="input-select-hidden secondary-select">
            <option value="Feature">Feature</option>
            <option value="Bug">Bug</option>
            <option value="Enhancement">Enhancement</option>
            <option value="DevOps">DevOps</option>
        </select>
        <label>Description</label>
        <textarea name="description" class="input-area" placeholder="Enter description..."></textarea>
    `;
    document.getElementById('entries').appendChild(block);
}

// add extra manual tasks rows while in auto mode
function addManualTaskRow() {
    const container = document.getElementById("extra-manual-tasks");

    const block = document.createElement("div");
    block.className = "entry-block"; 

    block.innerHTML = `
        <label for="extra_type">Tag</label>
        <button type="button" class="button-secondary" onclick="this.parentElement.remove()" style="float: right;">Remove Entry</button>
        <select name="extra_type" class="input-select primary-select" onchange="toggleSecondaryType(this)">
            <option value="Feature">Feature</option>
            <option value="Bug">Bug</option>
            <option value="Enhancement">Enhancement</option>
            <option value="DevOps">DevOps</option>
            <option value="Combination">Combination</option>
        </select>

        <label class="type-hidden-label" style="display: none;">Specify Your Combination of Tags</label>
        <select name="extra_type-hidden-1" class="input-select-hidden secondary-select">
            <option value="Feature">Feature</option>
            <option value="Bug">Bug</option>
            <option value="Enhancement">Enhancement</option>
            <option value="DevOps">DevOps</option>
        </select>

        <select name="extra_type-hidden-2" class="input-select-hidden secondary-select">
            <option value="Feature">Feature</option>
            <option value="Bug">Bug</option>
            <option value="Enhancement">Enhancement</option>
            <option value="DevOps">DevOps</option>
        </select>

        <label for="extra_description">Description</label>
        <textarea name="extra_description" class="input-area" placeholder="Enter description..."></textarea>
    `;

    // Insert before the "Add Another" button
    container.appendChild(block);

    // Activate toggle behavior for new row
    toggleSecondaryType(block.querySelector(".primary-select"));
}

// show loading on the generate button
function showLoading() {
    const button = document.getElementById("generate-btn");
    button.disabled = true;
    button.innerHTML = "Generating...";
    button.classList.add("loading");
}

// show/hide combo tag selections 
function toggleSecondaryType(select) {
    const block = select.closest('.entry-block');
    const show = select.value === "Combination";
    block.querySelector('.type-hidden-label').style.display = show ? "block" : "none";
    block.querySelectorAll('.secondary-select').forEach(sub => {
        sub.style.display = show ? "block" : "none";
    });
}