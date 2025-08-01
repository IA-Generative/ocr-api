import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.schemas import Base
from src.schemas.templates import (
    TemplateTable,
    TemplateForm,
    TemplateUpdateForm,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def template_table(db_session) -> TemplateTable:
    @contextmanager
    def fake_get_db():
        yield db_session

    return TemplateTable(get_db=fake_get_db)


def test_insert_new_template(template_table: TemplateTable):
    form_data = TemplateForm(
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
    )

    # Appelle la méthode
    result = template_table.insert_new_template(form_data=form_data)

    assert result is not None
    assert result.user_id == "user123"
    assert result.group_id == "group1"
    assert result.description == "Test Template"
    assert result.source_file == "source_file.pdf"
    assert result.source_task_id == "task123"
    assert result.page_number == 1
    assert result.vector == [1, 2, 3]
    assert result.extras["source"] == "test"
    assert isinstance(result.created_at, int)
    assert isinstance(result.updated_at, int)


def test_update_template(template_table: TemplateTable):
    new_template = template_table.insert_new_template(
        form_data=TemplateForm(
            user_id="user456",
            group_id="group1",
            description="Test Template",
            source_file="source_file.pdf",
            source_task_id="task123",
            page_number=1,
            vector=[1, 2, 3],
            extras={"source": "test"},
        )
    )

    assert new_template is not None

    update_form = TemplateUpdateForm(
        description="Updated Template",
        page_number=2,
        vector=[4, 5, 6],
        extras={"source": "updated"},
    )

    updated = template_table.update_template(template_id=new_template.id, form_data=update_form)

    assert updated is not None
    assert updated.id == new_template.id
    assert updated.description == "Updated Template"
    assert updated.page_number == 2
    assert updated.vector == [4, 5, 6]
    assert updated.extras == {"source": "updated"}

    not_found_updated = template_table.update_template(template_id="zzz", form_data=update_form)
    assert not_found_updated is None


def test_get_template_by_id(template_table: TemplateTable):
    # Step 1: Insert a template
    template = template_table.insert_new_template(
        form_data=TemplateForm(
            user_id="user789",
            group_id="group1",
            description="Test Template",
            source_file="source_file.pdf",
            source_task_id="task123",
            page_number=1,
            vector=[1, 2, 3],
            extras={"source": "test"},
        ),
    )

    assert template is not None

    # Step 2: Retrieve it
    retrieved = template_table.get_template_by_id(template.id)

    assert retrieved is not None
    assert retrieved.id == template.id
    assert retrieved.user_id == "user789"
    assert retrieved.group_id == "group1"
    assert retrieved.description == "Test Template"
    assert retrieved.source_file == "source_file.pdf"
    assert retrieved.source_task_id == "task123"
    assert retrieved.page_number == 1
    assert retrieved.vector == [1, 2, 3]
    assert retrieved.extras == {"source": "test"}


def test_get_template_by_invalid_id(template_table: TemplateTable):
    result = template_table.get_template_by_id("non-existent-id")
    assert result is None


def test_delete_template_by_id(template_table: TemplateTable):
    # Step 1: Create a template
    template = template_table.insert_new_template(
        form_data=TemplateForm(
            user_id="user123",
            group_id="group1",
            description="Test Template",
            source_file="source_file.pdf",
            source_task_id="task123",
            page_number=1,
            vector=[1, 2, 3],
            extras={"source": "test"},
        ),
    )

    assert template is not None

    # Step 2: Delete the template by id
    deleted_template = template_table.delete_template_by_id(template.id)

    # Step 3: Assertions
    assert deleted_template is not None
    assert deleted_template.id == template.id  # Ensure it's the same template

    # Step 4: Check that the template is deleted (it should return None now)
    template_after_deletion = template_table.get_template_by_id(template.id)
    assert template_after_deletion is None

    not_found_deleted_template = template_table.delete_template_by_id("template.id")
    assert not_found_deleted_template is None


def test_get_templates_by_user_id_with_pagination(template_table: TemplateTable):
    # Step 1: Insert 15 templates for user123
    for i in range(15):
        template_table.insert_new_template(
            form_data=TemplateForm(
                user_id="user123",
                group_id="group1",
                description=f"Test Template {i}",
                source_file="source_file.pdf",
                source_task_id="task123",
                page_number=1,
                vector=[1, 2, 3],
                extras={"source": "test"},
            ),
        )

    # Step 2: Retrieve first page with 5 templates per page
    templates_page_1 = template_table.get_templates_by_user_id(user_id="user123", page=1, page_size=5)
    assert templates_page_1 is not None
    assert len(templates_page_1) == 5  # First page should contain 5 templates

    # Step 2: Retrieve first page with 5 templates per page
    templates_page_1 = template_table.get_templates_by_user_id(user_id="user123", page=1, page_size=5)
    assert templates_page_1 is not None
    assert len(templates_page_1) == 5  # First page should contain 5 templates

    # Step 3: Retrieve second page with 5 templates per page
    templates_page_2 = template_table.get_templates_by_user_id(user_id="user123", page=2, page_size=5)
    assert templates_page_2 is not None
    assert len(templates_page_2) == 5  # Second page should also contain 5 templates

    # Step 4: Retrieve third page with 5 templates per page (which should be the last page)
    templates_page_3 = template_table.get_templates_by_user_id(user_id="user123", page=3, page_size=5)
    assert templates_page_3 is not None

    assert len(templates_page_3) == 5  # Last page should also contain 5 templates


def test_delete_template_by_user_id(template_table: TemplateTable):
    # Step 1: Insert 5 templates for user123
    for i in range(5):
        template_table.insert_new_template(
            form_data=TemplateForm(
                user_id="user1234",
                group_id="group1",
                description="Test Template",
                source_file="source_file.pdf",
                extras={"key": f"value_{i}"},
            ),
        )

    # Step 2: Delete all templates for user123
    deleted_templates = template_table.delete_templates_by_user_id("user1234")

    # Step 3: Assertions
    assert deleted_templates is not None
    assert len(deleted_templates) == 5  # All templates should be deleted

    # Step 4: Verify that templates are actually deleted (should return None when trying to get them)
    templates_after_deletion = template_table.get_templates_by_user_id(user_id="user1234", page=1, page_size=10)
    assert templates_after_deletion is None or len(templates_after_deletion) == 0  # No templates left for this user

    no_deleted_templates = template_table.delete_templates_by_user_id("user1234")
    assert no_deleted_templates is None


def test_template_group_id(template_table: TemplateTable):
    # Step 1: Insert a template with group_id
    template = template_table.insert_new_template(
        form_data=TemplateForm(
            user_id="user123",
            group_id="group_1",
            source_file="source_file.pdf",
        ),
    )

    assert template.group_id == "group_1"

    # Step 2: Retrieve templates by group_id
    templates = template_table.get_templates_by_group_id(group_id="group_1")

    assert templates is not None
    assert len(templates) == 1
    assert templates[0].id == template.id


def test_delete_templates_by_group_id(template_table: TemplateTable):
    # Step 1: Insert a template with group_id
    template = template_table.insert_new_template(
        form_data=TemplateForm(
            user_id="user123",
            description="Test Template",
            extras={"key": "value_0"},
            source_file="source_file.pdf",
            group_id="group_1",
        ),
    )
    # Step 2: Delete templates by group_id
    deleted_templates = template_table.delete_templates_by_group_id(group_id="group_1")

    assert deleted_templates is not None
    assert len(deleted_templates) == 1
    assert deleted_templates[0].id == template.id

    # Step 3: Verify that templates are actually deleted
    templates_after_deletion = template_table.get_templates_by_group_id(group_id="group_1")
    assert templates_after_deletion is None or len(templates_after_deletion) == 0
    assert template_table.get_template_by_id(template.id) is None  # Template should be deleted

    # Step 4: Try to delete again
    deleted_templates_again = template_table.delete_templates_by_group_id(group_id="group_1")
    assert deleted_templates_again is None or len(deleted_templates_again) == 0
