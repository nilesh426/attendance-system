// Helper function to toggle between attendance dates
function changeAttendanceDate(date) {
    window.location.href = `/attendance/view?date=${date}`;
}

// Function to mark all students as present
function markAllPresent() {
    const radioButtons = document.querySelectorAll('input[value="present"]');
    radioButtons.forEach(button => {
        button.checked = true;
    });
}

// Function to mark all students as absent
function markAllAbsent() {
    const radioButtons = document.querySelectorAll('input[value="absent"]');
    radioButtons.forEach(button => {
        button.checked = true;
    });
}

// Function to confirm attendance submission
function confirmSubmit() {
    return confirm("Are you sure you want to submit the attendance? This will overwrite any existing attendance for this date.");
}

// Function to confirm export
function confirmExport() {
    return confirm("Do you want to export this data to Excel?");
}

// Function to handle date change in attendance marking
function updateAttendanceDate() {
    const dateInput = document.getElementById('attendance-date');
    const departmentSelect = document.getElementById('department-filter');
    
    if (dateInput) {
        const departmentId = departmentSelect ? departmentSelect.value : 0;
        window.location.href = `/attendance/mark?date=${dateInput.value}&department_id=${departmentId}`;
    }
}

// Function to handle department filter change in attendance marking
function updateDepartmentFilter() {
    const dateInput = document.getElementById('attendance-date');
    const departmentSelect = document.getElementById('department-filter');
    
    if (departmentSelect) {
        const date = dateInput ? dateInput.value : new Date().toISOString().split('T')[0];
        window.location.href = `/attendance/mark?date=${date}&department_id=${departmentSelect.value}`;
    }
}

// Initialize datepickers and tooltips when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips everywhere
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    
    // Highlight the current date in the calendar if it exists
    const today = new Date().toISOString().split('T')[0];
    const currentDateElement = document.querySelector(`[data-date="${today}"]`);
    if (currentDateElement) {
        currentDateElement.classList.add('bg-primary');
    }
});
