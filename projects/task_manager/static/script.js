document.addEventListener('DOMContentLoaded', () => {
    const taskForm = document.getElementById('task-form');
    const taskTitleInput = document.getElementById('task-title');
    const taskDescInput = document.getElementById('task-description');
    const taskPriorityInput = document.getElementById('task-priority');
    const tasksContainer = document.getElementById('tasks-container');
    const taskCountSpan = document.getElementById('task-count');

    // Fetch and render all tasks
    const fetchTasks = async () => {
        try {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            renderTasks(tasks);
        } catch (error) {
            console.error('Error fetching tasks:', error);
        }
    };

    // Render tasks list in DOM
    const renderTasks = (tasks) => {
        tasksContainer.innerHTML = '';
        taskCountSpan.textContent = `${tasks.length} task${tasks.length !== 1 ? 's' : ''}`;

        if (tasks.length === 0) {
            tasksContainer.innerHTML = `
                <div class="glass-card text-center" style="padding: 40px; text-align: center; color: #9ca3af;">
                    <i class="fa-regular fa-clipboard" style="font-size: 2.5rem; margin-bottom: 15px; display: block; opacity: 0.5;"></i>
                    No tasks found. Add a new task to get started!
                </div>
            `;
            return;
        }

        tasks.forEach(task => {
            const card = document.createElement('div');
            card.className = `glass-card task-card ${task.priority.toLowerCase()} ${task.completed ? 'completed' : ''}`;
            card.innerHTML = `
                <div class="task-info">
                    <h3>${escapeHTML(task.title)}</h3>
                    ${task.description ? `<p>${escapeHTML(task.description)}</p>` : ''}
                </div>
                <div class="task-actions">
                    <label class="checkbox-container">
                        <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTaskStatus(${task.id})">
                        <span class="checkmark">
                            <i class="fa-solid fa-check"></i>
                        </span>
                    </label>
                    <button class="delete-btn" onclick="deleteTaskItem(${task.id})">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            `;
            tasksContainer.appendChild(card);
        });
    };

    // Create a new task
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = taskTitleInput.value.trim();
        const description = taskDescInput.value.trim();
        const priority = taskPriorityInput.value;

        if (!title) return;

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title, description, priority })
            });

            if (response.ok) {
                taskTitleInput.value = '';
                taskDescInput.value = '';
                taskPriorityInput.value = 'Medium';
                fetchTasks();
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Error creating task:', error);
        }
    });

    // Toggle complete status
    window.toggleTaskStatus = async (taskId) => {
        try {
            const response = await fetch(`/api/tasks/${taskId}/toggle`, {
                method: 'POST'
            });
            if (response.ok) {
                fetchTasks();
            }
        } catch (error) {
            console.error('Error toggling task:', error);
        }
    };

    // Delete a task item
    window.deleteTaskItem = async (taskId) => {
        if (!confirm('Are you sure you want to delete this task?')) return;
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                fetchTasks();
            }
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    };

    // Utility to prevent HTML injection
    const escapeHTML = (str) => {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    };

    // Initial load
    fetchTasks();
});
