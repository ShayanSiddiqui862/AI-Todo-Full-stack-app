from sqlmodel import Session, select
from backend.src.models.task import Task
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '001_advanced_features'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to tasks table
    op.add_column('task', sa.Column('priority', sa.String(10), server_default='medium'))
    op.execute("ALTER TABLE task ADD CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high'))")

    op.add_column('task', sa.Column('tags', sa.ARRAY(sa.String)))
    op.execute("ALTER TABLE task ALTER COLUMN tags SET DEFAULT '{}'")

    op.add_column('task', sa.Column('due_date', sa.DateTime(timezone=True)))
    op.add_column('task', sa.Column('remind_at', sa.DateTime(timezone=True)))
    op.add_column('task', sa.Column('recurrence_type', sa.String(20), server_default='none'))
    op.execute("ALTER TABLE task ADD CONSTRAINT chk_recurrence CHECK (recurrence_type IN ('none', 'daily', 'weekly', 'monthly'))")

    op.add_column('task', sa.Column('recurrence_interval', sa.Integer, server_default='1'))

    # Create new tables
    op.create_table('taskevents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('scheduledjobs',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('executed', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient searching
    op.create_index('idx_task_title_gin', 'task', [sa.text('to_tsvector(\'english\', title)')], postgresql_using='gin')
    op.create_index('idx_task_description_gin', 'task', [sa.text('to_tsvector(\'english\', coalesce(description, \'\'))')], postgresql_using='gin')
    op.create_index('idx_task_tags_gin', 'task', ['tags'], postgresql_using='gin')
    op.create_index('idx_task_priority', 'task', ['priority'])
    op.create_index('idx_task_due_date', 'task', ['due_date'])
    op.create_index('idx_task_user_id', 'task', ['user_id'])


def downgrade():
    op.drop_table('scheduledjobs')
    op.drop_table('taskevents')

    op.drop_constraint('chk_recurrence', 'task', type_='check')
    op.drop_constraint('chk_priority', 'task', type_='check')

    op.drop_column('task', 'recurrence_interval')
    op.drop_column('task', 'recurrence_type')
    op.drop_column('task', 'remind_at')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'tags')
    op.drop_column('task', 'priority')