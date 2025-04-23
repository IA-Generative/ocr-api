from src.schemas.task_stats import task_stat_table, TaskStatsForm


def test_insert_and_get_task():
    form = TaskStatsForm(type="test-type", status="queued", percentage=0.5)

    task = task_stat_table.insert_new_task(user_id="user-1", form_data=form)

    assert task is not None
    assert task.type == "test-type"
    assert task.status == "queued"

    fetched = task_stat_table.get_task_by_id(task.id)
    assert fetched is not None
    assert fetched.id == task.id


def test_up_vote():
    form = TaskStatsForm(type="type", status="queued", percentage=0.0)
    task = task_stat_table.insert_new_task("user-1", form)

    original_votes = task.up_vote
    updated = task_stat_table.up_vote(task.id)

    assert updated.up_vote == original_votes + 1


def test_down_vote():

    form = TaskStatsForm(type="type", status="queued", percentage=0.0)
    task = task_stat_table.insert_new_task("user-1", form)

    original_votes = task.down_vote
    updated = task_stat_table.down_vote(task.id)

    assert updated.down_vote == original_votes + 1


def test_update_task():
    form = TaskStatsForm(type="init", status="queued", percentage=0.0)
    task = task_stat_table.insert_new_task("user-1", form)

    update_form = TaskStatsForm(type="updated", status="running", percentage=0.9)
    updated_task = task_stat_table.update_task(task.id, update_form)

    assert updated_task.type == "updated"
    assert updated_task.status == "running"
    assert updated_task.percentage == 0.9


def test_delete_task():
    form = TaskStatsForm(type="type", status="queued", percentage=0.0)
    task = task_stat_table.insert_new_task("user-1", form)

    deleted = task_stat_table.delete_task_by_id(task.id)
    assert deleted.id == task.id

    should_be_none = task_stat_table.get_task_by_id(task.id)
    assert should_be_none is None
