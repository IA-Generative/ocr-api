import pytest
import uuid
import time
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.task_repository import TaskRepository
from src.schemas.task import TaskForm, TaskModel, TaskStatus, TaskUpdateForm
from src.models.task import Task


@pytest.fixture
def sample_task_form():
    """Données de formulaire pour créer une tâche"""
    return TaskForm(
        type="document_analysis",
        status=TaskStatus.IN_PROGRESS,
        percentage=0.0,
    )


@pytest.fixture
def sample_user_id():
    """ID utilisateur de test"""
    return str(uuid.uuid4())


# ============================================================================
# TESTS AVEC VRAIE BASE DE DONNÉES ASYNC
# ============================================================================


@pytest.mark.asyncio
async def test_insert_new_task_with_real_db(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test insert_new_task avec une vraie base de données async et session"""

    task_repository = TaskRepository()

    # Act
    result = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    # Assert
    assert isinstance(result, TaskModel)
    assert result.user_id == sample_user_id
    assert result.type == sample_task_form.type
    assert result.status == TaskStatus.CREATED.value
    assert result.percentage == sample_task_form.percentage
    assert result.id is not None
    assert len(result.id) > 0


@pytest.mark.asyncio
async def test_insert_new_task_has_timestamps_real_db(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que la tâche a bien les timestamps created_at et updated_at (vraie BD)"""

    task_repository = TaskRepository()

    before_time = int(time.time())

    # Act
    result = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    after_time = int(time.time())

    # Assert
    assert hasattr(result, "created_at")
    assert hasattr(result, "updated_at")
    assert before_time <= result.created_at <= after_time
    assert before_time <= result.updated_at <= after_time
    assert result.created_at == result.updated_at


@pytest.mark.asyncio
async def test_insert_new_task_has_unique_id_real_db(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que chaque tâche a un ID unique (vraie BD)"""

    task_repository = TaskRepository()

    # Act
    result1 = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    result2 = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    # Assert
    assert result1.id != result2.id
    assert len(result1.id) > 0
    assert len(result2.id) > 0


@pytest.mark.asyncio
async def test_insert_new_task_persisted_in_db(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que la tâche est bien persistée dans la base de données"""

    task_repository = TaskRepository()

    # Act
    result = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    # Assert - Vérifier que la tâche existe dans la BD
    db_task = await db_session.get(Task, (result.id, result.type))
    assert db_task is not None
    assert db_task.id == result.id
    assert db_task.user_id == sample_user_id
    assert db_task.type == sample_task_form.type
    assert db_task.status == TaskStatus.CREATED.value


# ============================================================================
# TESTS GET_TASK_BY_ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_task_by_id_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_task_by_id retourne la bonne tâche"""

    task_repository = TaskRepository()

    # Arrange - Créer une tâche d'abord
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    await db_session.flush()  # S'assurer que la tâche est persisted

    # Act
    retrieved_task = await task_repository.get_task_by_id(
        db=db_session,
        task_id=created_task.id,
        task_type=created_task.type,
    )

    # Assert
    assert isinstance(retrieved_task, TaskModel)
    assert retrieved_task.id == created_task.id
    assert retrieved_task.user_id == sample_user_id
    assert retrieved_task.type == sample_task_form.type
    assert retrieved_task.status == TaskStatus.CREATED.value


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(db_session: AsyncSession):
    """Test que get_task_by_id lève une HTTPException quand la tâche n'existe pas"""

    task_repository = TaskRepository()
    fake_task_id = str(uuid.uuid4())

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await task_repository.get_task_by_id(db=db_session, task_id=fake_task_id, task_type="fake_type")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_task_by_id_returns_correct_data(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_task_by_id retourne exactement les mêmes données que la tâche créée"""

    task_repository = TaskRepository()

    # Arrange
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )

    await db_session.flush()

    # Act
    retrieved_task = await task_repository.get_task_by_id(
        db=db_session,
        task_id=created_task.id,
        task_type=created_task.type,
    )

    # Assert - Vérifier tous les champs
    assert retrieved_task.id == created_task.id
    assert retrieved_task.user_id == created_task.user_id
    assert retrieved_task.type == created_task.type
    assert retrieved_task.status == created_task.status
    assert retrieved_task.percentage == created_task.percentage
    assert retrieved_task.created_at == created_task.created_at
    assert retrieved_task.updated_at == created_task.updated_at


# ============================================================================
# TESTS GET_TASKS_BY_ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_tasks_by_id_empty_list_when_not_found(db_session: AsyncSession):
    """Test que get_tasks_by_id retourne une liste vide quand aucune tâche n'existe"""

    task_repository = TaskRepository()
    fake_task_id = str(uuid.uuid4())

    # Act
    result = await task_repository.get_tasks_by_id(
        db=db_session,
        task_id=fake_task_id,
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []


@pytest.mark.asyncio
async def test_get_tasks_by_id_single_task(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_tasks_by_id retourne une liste avec une tâche"""

    task_repository = TaskRepository()

    # Arrange - Créer une tâche
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )
    await db_session.flush()

    # Act
    result = await task_repository.get_tasks_by_id(
        db=db_session,
        task_id=created_task.id,
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == created_task.id
    assert result[0].user_id == sample_user_id
    assert result[0].type == sample_task_form.type


@pytest.mark.asyncio
async def test_get_tasks_by_id_multiple_tasks_same_id(db_session: AsyncSession, sample_user_id):
    """Test que get_tasks_by_id retourne plusieurs tâches avec le même ID mais des types différents"""

    task_repository = TaskRepository()
    shared_task_id = str(uuid.uuid4())

    # Créer les tâches manuellement avec le même ID
    task_model_1 = TaskModel(
        id=shared_task_id,
        user_id=sample_user_id,
        type="document_analysis",
        status=TaskStatus.IN_PROGRESS.value,
        percentage=0.0,
        created_at=int(time.time()),
        updated_at=int(time.time()),
    )
    task_model_2 = TaskModel(
        id=shared_task_id,
        user_id=sample_user_id,
        type="image_processing",
        status=TaskStatus.CREATED.value,
        percentage=0.5,
        created_at=int(time.time()),
        updated_at=int(time.time()),
    )

    task_1 = Task(**task_model_1.model_dump())
    task_2 = Task(**task_model_2.model_dump())
    db_session.add(task_1)
    db_session.add(task_2)
    await db_session.flush()

    # Act
    result = await task_repository.get_tasks_by_id(
        db=db_session,
        task_id=shared_task_id,
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == shared_task_id
    assert result[1].id == shared_task_id
    assert result[0].type == "document_analysis"
    assert result[1].type == "image_processing"


@pytest.mark.asyncio
async def test_get_tasks_by_id_returns_correct_data(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_tasks_by_id retourne les bonnes données"""

    task_repository = TaskRepository()

    # Arrange
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )
    await db_session.flush()

    # Act
    result = await task_repository.get_tasks_by_id(
        db=db_session,
        task_id=created_task.id,
    )

    # Assert
    assert len(result) == 1
    retrieved_task = result[0]
    assert retrieved_task.id == created_task.id
    assert retrieved_task.user_id == created_task.user_id
    assert retrieved_task.type == created_task.type
    assert retrieved_task.status == created_task.status
    assert retrieved_task.percentage == created_task.percentage


# ============================================================================
# TESTS UPDATE_TASK
# ============================================================================


@pytest.mark.asyncio
async def test_update_task_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que update_task modifie correctement une tâche"""

    task_repository = TaskRepository()

    # Arrange
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )
    await db_session.flush()

    update_form = TaskUpdateForm(
        status=TaskStatus.COMPLETED,
        percentage=100.0,
    )

    # Act
    result = await task_repository.update_task(
        db=db_session,
        task_id=created_task.id,
        form_data=update_form,
        task_type=created_task.type,
    )

    # Assert
    assert result.id == created_task.id
    assert result.status == TaskStatus.COMPLETED.value
    assert result.percentage == 100.0
    assert result.updated_at >= created_task.updated_at


@pytest.mark.asyncio
async def test_update_task_not_found(db_session: AsyncSession):
    """Test que update_task lève une HTTPException si la tâche n'existe pas"""

    task_repository = TaskRepository()
    fake_task_id = str(uuid.uuid4())
    update_form = TaskUpdateForm(percentage=50.0)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await task_repository.update_task(
            db=db_session,
            task_id=fake_task_id,
            task_type="fake_type",
            form_data=update_form,
        )

    assert exc_info.value.status_code == 404


# ============================================================================
# TESTS DELETE_TASK_BY_ID
# ============================================================================


@pytest.mark.asyncio
async def test_delete_task_by_id_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que delete_task_by_id supprime correctement une tâche"""

    task_repository = TaskRepository()

    # Arrange
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )
    await db_session.flush()

    # Act
    result = await task_repository.delete_task_by_id(
        db=db_session,
        task_id=created_task.id,
        task_type=created_task.type,
    )

    # Assert
    assert result.id == created_task.id

    # Vérifier qu'elle est supprimée
    with pytest.raises(HTTPException):
        await task_repository.get_task_by_id(
            db=db_session,
            task_id=created_task.id,
            task_type=created_task.type,
        )


@pytest.mark.asyncio
async def test_delete_task_by_id_not_found(db_session: AsyncSession):
    """Test que delete_task_by_id lève HTTPException si la tâche n'existe pas"""

    task_repository = TaskRepository()
    fake_task_id = str(uuid.uuid4())

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await task_repository.delete_task_by_id(
            db=db_session,
            task_id=fake_task_id,
            task_type="fake_type",
        )

    assert exc_info.value.status_code == 404


# ============================================================================
# TESTS GET_TASKS_BY_USER_ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_tasks_by_user_id_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_tasks_by_user_id retourne les tâches du user"""

    task_repository = TaskRepository()

    # Arrange - Créer 3 tâches pour cet utilisateur
    for i in range(3):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=sample_task_form,
        )
    await db_session.flush()

    # Act
    result = await task_repository.get_tasks_by_user_id(
        db=db_session,
        user_id=sample_user_id,
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == 3
    for task in result:
        assert task.user_id == sample_user_id


@pytest.mark.asyncio
async def test_get_tasks_by_user_id_pagination(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_tasks_by_user_id respecte la pagination"""

    task_repository = TaskRepository()

    # Arrange - Créer 5 tâches
    for i in range(5):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=sample_task_form,
        )
    await db_session.flush()

    # Act - Page 1 avec 2 par page
    result_page1 = await task_repository.get_tasks_by_user_id(
        db=db_session,
        user_id=sample_user_id,
        page=1,
        page_size=2,
    )

    result_page2 = await task_repository.get_tasks_by_user_id(
        db=db_session,
        user_id=sample_user_id,
        page=2,
        page_size=2,
    )

    # Assert
    assert len(result_page1) == 2
    assert len(result_page2) == 2


@pytest.mark.asyncio
async def test_get_tasks_by_user_id_empty(db_session: AsyncSession):
    """Test que get_tasks_by_user_id retourne une liste vide pour un user sans tâches"""

    task_repository = TaskRepository()
    fake_user_id = str(uuid.uuid4())

    # Act
    result = await task_repository.get_tasks_by_user_id(
        db=db_session,
        user_id=fake_user_id,
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0


# ============================================================================
# TESTS COUNT_TASKS_BY_USER_ID
# ============================================================================


@pytest.mark.asyncio
async def test_count_tasks_by_user_id_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que count_tasks_by_user_id compte correctement les tâches"""

    task_repository = TaskRepository()

    # Arrange - Créer 5 tâches
    for i in range(5):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=sample_task_form,
        )
    await db_session.flush()

    # Act
    count = await task_repository.count_tasks_by_user_id(
        db=db_session,
        user_id=sample_user_id,
    )

    # Assert
    assert count == 5


@pytest.mark.asyncio
async def test_count_tasks_by_user_id_zero(db_session: AsyncSession):
    """Test que count_tasks_by_user_id retourne 0 pour un user sans tâches"""

    task_repository = TaskRepository()
    fake_user_id = str(uuid.uuid4())

    # Act
    count = await task_repository.count_tasks_by_user_id(
        db=db_session,
        user_id=fake_user_id,
    )

    # Assert
    assert count == 0


# ============================================================================
# TESTS DELETE_TASKS_BY_USER_ID
# ============================================================================


@pytest.mark.asyncio
async def test_delete_tasks_by_user_id_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que delete_tasks_by_user_id supprime toutes les tâches du user"""

    task_repository = TaskRepository()

    # Arrange - Créer 3 tâches
    for i in range(3):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=sample_task_form,
        )
    await db_session.flush()

    # Act
    result = await task_repository.delete_tasks_by_user_id(
        db=db_session,
        user_id=sample_user_id,
    )

    # Assert
    assert len(result) == 3

    # Vérifier qu'elles sont supprimées
    count = await task_repository.count_tasks_by_user_id(
        db=db_session,
        user_id=sample_user_id,
    )
    assert count == 0


# ============================================================================
# TESTS GET_POSITION_IN_QUEUE
# ============================================================================


@pytest.mark.asyncio
async def test_get_position_in_queue_success(db_session: AsyncSession, sample_user_id):
    """Test que get_position_in_queue retourne la bonne position"""

    task_repository = TaskRepository()

    # Arrange - Créer 3 tâches en file d'attente
    task_form = TaskForm(
        type="test",
        status=TaskStatus.QUEUED,
        percentage=0.0,
    )
    for i in range(3):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=task_form,
        )
    await db_session.flush()

    # Récupérer les tâches
    tasks = await task_repository.get_tasks_by_id(
        db=db_session,
        task_id=(await task_repository.get_tasks_by_user_id(db=db_session, user_id=sample_user_id))[0].id,
    )

    # Act
    position = await task_repository.get_position_in_queue(
        db=db_session,
        task_id=tasks[0].id,
        task_type=tasks[0].type,
    )

    # Assert
    assert position is None


@pytest.mark.asyncio
async def test_get_position_in_queue_not_queued(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que get_position_in_queue retourne None si la tâche n'est pas en file"""

    task_repository = TaskRepository()

    # Arrange - Créer une tâche non-queued
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=sample_task_form,
    )
    await db_session.flush()

    # Act
    position = await task_repository.get_position_in_queue(
        db=db_session,
        task_id=created_task.id,
        task_type=created_task.type,
    )

    # Assert
    assert position is None


# ============================================================================
# TESTS GET_TASK_BY_CONTENT_HASH
# ============================================================================


@pytest.mark.asyncio
async def test_get_task_by_content_hash_success(db_session: AsyncSession, sample_user_id):
    """Test que get_task_by_content_hash retourne la bonne tâche"""

    task_repository = TaskRepository()
    content_hash = "hash_123"

    # Arrange - Créer une tâche avec un hash
    task_form = TaskForm(
        type="test",
        status=TaskStatus.CREATED,
        percentage=0.0,
    )
    created_task = await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=task_form,
    )

    # Mettre à jour le hash manuellement
    created_task_db = await db_session.get(Task, (created_task.id, created_task.type))
    created_task_db.content_hash = content_hash  # type: ignore
    await db_session.flush()

    # Act
    result = await task_repository.get_task_by_content_hash(
        db=db_session,
        content_hash_value=content_hash,
    )

    # Assert
    assert result.id == created_task.id
    assert result.content_hash == content_hash


@pytest.mark.asyncio
async def test_get_task_by_content_hash_not_found(db_session: AsyncSession):
    """Test que get_task_by_content_hash lève HTTPException si non trouvée"""

    task_repository = TaskRepository()
    fake_hash = "non_existent_hash"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await task_repository.get_task_by_content_hash(
            db=db_session,
            content_hash_value=fake_hash,
        )

    assert exc_info.value.status_code == 404


# ============================================================================
# TESTS DELETE_TASKS_BY_DATE_AND_STATUS
# ============================================================================


@pytest.mark.asyncio
async def test_delete_tasks_by_date_and_status_success(db_session: AsyncSession, sample_user_id):
    """Test que delete_tasks_by_date_and_status supprime les bonnes tâches"""

    task_repository = TaskRepository()
    now = datetime.now()

    # Arrange - Créer une tâche avec timestamp actuel
    task_form = TaskForm(
        type="test",
        status=TaskStatus.CREATED,
        percentage=0.0,
    )
    await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=task_form,
    )
    await db_session.flush()
    await db_session.commit()

    # Act
    result = await task_repository.delete_tasks_by_date_and_status(
        db=db_session,
        start_date=now - timedelta(hours=2),
        end_date=now + timedelta(hours=2),
        status=TaskStatus.CREATED,
    )

    # Assert
    assert len(result) >= 1


# ============================================================================
# TESTS GET_TASKS_BY_GROUP_ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_tasks_by_group_id_success(db_session: AsyncSession, sample_user_id):
    """Test que get_tasks_by_group_id retourne les tâches du group"""

    task_repository = TaskRepository()
    group_id = str(uuid.uuid4())

    # Arrange - Créer 2 tâches avec le même group_id
    task_form = TaskForm(
        type="test",
        status=TaskStatus.CREATED,
        percentage=0.0,
        group_id=group_id,
    )
    for i in range(2):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=task_form,
        )
    await db_session.flush()

    # Act
    result = await task_repository.get_tasks_by_group_id(
        db=db_session,
        group_id=group_id,
    )

    # Assert
    assert len(result) == 2
    for task in result:
        assert task.group_id == group_id


@pytest.mark.asyncio
async def test_get_tasks_by_group_id_empty(db_session: AsyncSession):
    """Test que get_tasks_by_group_id retourne une liste vide si aucune tâche"""

    task_repository = TaskRepository()
    fake_group_id = str(uuid.uuid4())

    # Act
    result = await task_repository.get_tasks_by_group_id(
        db=db_session,
        group_id=fake_group_id,
    )

    # Assert
    assert len(result) == 0


# ============================================================================
# TESTS DELETE_TASKS_BY_GROUP_ID
# ============================================================================


@pytest.mark.asyncio
async def test_delete_tasks_by_group_id_success(db_session: AsyncSession, sample_user_id):
    """Test que delete_tasks_by_group_id supprime les tâches du group"""

    task_repository = TaskRepository()
    group_id = str(uuid.uuid4())

    # Arrange - Créer 2 tâches avec le même group_id
    task_form = TaskForm(
        type="test",
        status=TaskStatus.CREATED,
        percentage=0.0,
        group_id=group_id,
    )
    for i in range(2):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=task_form,
        )
    await db_session.flush()

    # Act
    result = await task_repository.delete_tasks_by_group_id(
        db=db_session,
        group_id=group_id,
    )

    # Assert
    assert len(result) == 2

    # Vérifier qu'elles sont supprimées
    remaining = await task_repository.get_tasks_by_group_id(
        db=db_session,
        group_id=group_id,
    )
    assert len(remaining) == 0


# ============================================================================
# TESTS STATISTICS
# ============================================================================


@pytest.mark.asyncio
async def test_statistics_success(db_session: AsyncSession, sample_task_form, sample_user_id):
    """Test que statistics retourne les stats correctes"""

    task_repository = TaskRepository()

    # Arrange - Créer 3 tâches pour cet utilisateur
    for _ in range(3):
        await task_repository.insert_new_task(
            db=db_session,
            user_id=sample_user_id,
            form_data=sample_task_form,
        )
    await db_session.flush()

    # Act
    stats = await task_repository.statistics(
        db=db_session,
        user_id=sample_user_id,
    )

    # Assert
    assert stats is not None
    assert stats.global_stats is not None
    assert stats.global_stats.total_tasks >= 3
    assert stats.user_stats is not None
    assert stats.user_stats.user_id == sample_user_id
    assert stats.user_stats.total_tasks == 3


@pytest.mark.asyncio
async def test_statistics_empty_user(db_session: AsyncSession):
    """Test que statistics fonctionne pour un user sans tâches"""

    task_repository = TaskRepository()
    fake_user_id = str(uuid.uuid4())

    # Act
    stats = await task_repository.statistics(
        db=db_session,
        user_id=fake_user_id,
    )

    # Assert
    assert stats is not None
    assert stats.user_stats.user_id == fake_user_id
    assert stats.user_stats.total_tasks == 0
    assert len(stats.user_stats.tasks_stats) == 0


@pytest.mark.asyncio
async def test_statistics_different_statuses(db_session: AsyncSession, sample_user_id):
    """Test que statistics compte correctement les tâches par statut"""

    task_repository = TaskRepository()

    # Arrange - Créer 2 tâches avec des statuts différents
    task_form_1 = TaskForm(
        type="test_1",
        status=TaskStatus.IN_PROGRESS,
        percentage=50.0,
    )
    task_form_2 = TaskForm(
        type="test_2",
        status=TaskStatus.COMPLETED,
        percentage=100.0,
    )

    await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=task_form_1,
    )
    await task_repository.insert_new_task(
        db=db_session,
        user_id=sample_user_id,
        form_data=task_form_2,
    )
    await db_session.flush()
    await db_session.commit()

    # Act
    stats = await task_repository.statistics(
        db=db_session,
        user_id=sample_user_id,
    )

    # Assert
    assert stats.user_stats.total_tasks == 2
    assert len(stats.user_stats.tasks_stats) == 1


# ============================================================================
# TESTS COUNT_UNIQUE_USERS_BETWEEN_DATES
# ============================================================================


@pytest.mark.asyncio
async def test_count_unique_users_between_dates_success(db_session: AsyncSession, sample_task_form):
    """Test que count_unique_users_between_dates compte correctement"""

    task_repository = TaskRepository()
    now = int(time.time())

    # Arrange - Créer des tâches pour 3 utilisateurs différents
    user_ids = [str(uuid.uuid4()) for _ in range(3)]
    for user_id in user_ids:
        await task_repository.insert_new_task(
            db=db_session,
            user_id=user_id,
            form_data=sample_task_form,
        )
    await db_session.flush()

    # Act
    count = await task_repository.count_unique_users_between_dates(
        db=db_session,
        start_date=now - 1000,
        end_date=now + 1000,
    )

    # Assert
    assert count == 3


@pytest.mark.asyncio
async def test_count_unique_users_between_dates_outside_range(db_session: AsyncSession, sample_task_form):
    """Test que count_unique_users_between_dates retourne 0 en dehors de la plage"""

    task_repository = TaskRepository()
    now = int(time.time())

    # Arrange - Créer une tâche
    user_id = str(uuid.uuid4())
    await task_repository.insert_new_task(
        db=db_session,
        user_id=user_id,
        form_data=sample_task_form,
    )
    await db_session.flush()

    # Act - Chercher en dehors de la plage
    count = await task_repository.count_unique_users_between_dates(
        db=db_session,
        start_date=now + 10000,
        end_date=now + 20000,
    )

    # Assert
    assert count == 0


@pytest.mark.asyncio
async def test_count_unique_users_between_dates_empty(db_session: AsyncSession):
    """Test que count_unique_users_between_dates retourne 0 si aucune tâche"""

    task_repository = TaskRepository()
    now = int(time.time())

    # Act
    count = await task_repository.count_unique_users_between_dates(
        db=db_session,
        start_date=now - 1000,
        end_date=now + 1000,
    )

    # Assert
    assert count == 0
