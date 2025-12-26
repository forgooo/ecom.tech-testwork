from alembic import op
import sqlalchemy as sa


revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'grades',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('grade', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.CheckConstraint('grade >= 2 AND grade <= 5')
    )
    op.create_index('idx_grades_full_name', 'grades', ['full_name'])
    op.create_index('idx_grades_grade', 'grades', ['grade'])
    op.create_index('idx_grades_subject', 'grades', ['subject'])
    op.create_index('idx_grades_full_name_grade', 'grades', ['full_name', 'grade'])

def downgrade():
    op.drop_table('grades')
