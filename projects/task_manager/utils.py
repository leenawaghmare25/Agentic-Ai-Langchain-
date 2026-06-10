def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = not task.completed
    db.session.commit()
