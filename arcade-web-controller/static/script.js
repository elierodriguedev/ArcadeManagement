document.addEventListener('DOMContentLoaded', function() {
    const machinesTableBody = document.querySelector('#machines-table tbody');
    const refreshButton = document.getElementById('refresh-button');

    // Function to fetch and display machine data
    function fetchAndDisplayMachines() {
        fetch('/api/discovered_machines')
            .then(response => response.json())
            .then(data => {
                // Clear existing table rows
                machinesTableBody.innerHTML = '';

                // Populate table with new data
                data.forEach(machine => {
                    const row = machinesTableBody.insertRow();
                    row.insertCell().textContent = machine.hostname;
                    row.insertCell().textContent = machine.type;
                    row.insertCell().textContent = machine.status;
                    row.insertCell().textContent = machine.last_seen;
                    row.insertCell().textContent = machine.version;
                    row.insertCell().textContent = machine.hostname; // Assuming hostname is also the name for now
                    row.insertCell().textContent = machine.disk_free_gb;
                    row.insertCell().textContent = machine.cpu_percent;
                    row.insertCell().textContent = machine.ram_percent;
                    row.insertCell().textContent = machine.bigbox_running;

                    // Add Actions cell (placeholder for now)
                    const actionsCell = row.insertCell();
                    actionsCell.textContent = '...'; // Placeholder text

                    // Store hostname in a data attribute for easy access
                    row.dataset.hostname = machine.hostname;

                    // Add a class based on status for styling
                    if (machine.status === 'Offline') {
                        row.classList.add('offline');
                    }
                });

                // Add double-click event listener to table rows
                machinesTableBody.querySelectorAll('tr').forEach(row => {
                    row.addEventListener('dblclick', function() {
                        const hostname = this.dataset.hostname;
                        if (hostname) {
                            const agentUrl = `http://${hostname}:5151/`;
                            window.open(agentUrl, '_blank');
                        }
                    });
                });

            })
            .catch(error => {
                console.error('Error fetching machine data:', error);
                // Optionally display an error message in the UI
            });
    }

    // Fetch data initially
    fetchAndDisplayMachines();

    // Refresh data periodically (e.g., every 5 seconds)
    setInterval(fetchAndDisplayMachines, 5000);

    // Add event listener to the refresh button (optional, as we have periodic refresh)
    if (refreshButton) {
        refreshButton.addEventListener('click', fetchAndDisplayMachines);
    }

    // Tab switching logic
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function showTab(tabId) {
        tabPanes.forEach(pane => {
            pane.classList.add('hidden');
        });
        document.getElementById(tabId).classList.remove('hidden');
    }

    function activateTabButton(button) {
        tabButtons.forEach(btn => {
            btn.classList.remove('border-blue-500', 'border-b-2', 'text-blue-500');
            btn.classList.add('border-transparent', 'text-gray-600');
        });
        button.classList.add('border-blue-500', 'border-b-2', 'text-blue-500');
        button.classList.remove('border-transparent', 'text-gray-600');
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            showTab(`tab-${tabId}`);
            activateTabButton(this);
        });
    });

    // Show the default tab (e.g., Machines tab) on page load
    const defaultTabButton = document.querySelector('.tab-button[data-tab="machines"]');
    if (defaultTabButton) {
        showTab('tab-machines');
        activateTabButton(defaultTabButton);
    }


    // --- Placeholder for Modal/Layout Edit functionality ---
    // You would add code here to handle opening/closing the modal,
    // fetching/saving layout data, etc.
    // const layoutModal = document.getElementById('layout-modal');
    // const closeButton = layoutModal.querySelector('.close-button');
    // const saveLayoutButton = document.getElementById('save-layout-button');

    // // Example: Open modal (you'd trigger this from an "Edit Layout" button in the table)
    // function openLayoutModal(machineHostname) {
    //     document.getElementById('modal-machine-name').textContent = machineHostname;
    //     // Fetch layout data for the machine and populate the form
    //     // ...
    //     layoutModal.style.display = 'block';
    // }

    // // Example: Close modal
    // closeButton.onclick = function() {
    //     layoutModal.style.display = 'none';
    // }

    // // Example: Save layout
    // saveLayoutButton.onclick = function() {
    //     // Gather form data and send PUT request to /api/machines/<hostname>/control-layout
    //     // ...
    //     layoutModal.style.display = 'none'; // Close on save (or on success)
    // }

    // // Close modal if user clicks outside of it
    // window.onclick = function(event) {
    //     if (event.target == layoutModal) {
    //         layoutModal.style.display = 'none';
    //     }
    // }
});

document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('tab-active'));
            // Add active class to the clicked button
            button.classList.add('tab-active');

            // Hide all tab panes
            tabPanes.forEach(pane => pane.classList.add('hidden'));
            // Show the target tab pane
            const targetTab = button.dataset.tab;
            document.getElementById(`tab-${targetTab}`).classList.remove('hidden');
        });
    });

    // Set the initial active tab and display the corresponding pane
    const initialTabButton = document.querySelector('.tab-button.tab-active');
    if (initialTabButton) {
        const targetTab = initialTabButton.dataset.tab;
        document.getElementById(`tab-${targetTab}`).classList.remove('hidden');
    } else {
        // If no initial active tab is set, default to the first tab
        if (tabButtons.length > 0) {
            tabButtons[0].classList.add('tab-active');
            const targetTab = tabButtons[0].dataset.tab;
            document.getElementById(`tab-${targetTab}`).classList.remove('hidden');
        }
    }
});
