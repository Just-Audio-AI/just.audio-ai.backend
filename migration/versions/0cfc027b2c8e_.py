"""

Revision ID: 0cfc027b2c8e
Revises: 67d7c990dd55
Create Date: 2025-04-22 17:48:05.801401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cfc027b2c8e'
down_revision: Union[str, None] = '67d7c990dd55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Сначала создаем уникальный индекс для поля id в таблице user_files
    # Это необходимо, так как внешний ключ должен ссылаться на уникальное поле
    conn = op.get_bind()
    conn.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS uq_user_files_id ON user_files (id)"))
    
    # Создаем таблицу chat_sessions
    op.create_table('chat_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_file_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Добавляем внешние ключи после создания таблицы
    op.create_foreign_key(
        'fk_chat_sessions_user_file_id',
        'chat_sessions', 'user_files',
        ['user_file_id'], ['id'],
        ondelete='CASCADE'
    )
    
    op.create_foreign_key(
        'fk_chat_sessions_user_id',
        'chat_sessions', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Создаем индексы для chat_sessions
    op.create_index(op.f('ix_chat_sessions_user_file_id'), 'chat_sessions', ['user_file_id'], unique=False)
    op.create_index(op.f('ix_chat_sessions_user_id'), 'chat_sessions', ['user_id'], unique=False)
    
    # Создаем таблицу chat_messages
    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('sender', sa.String(), nullable=False, comment="Enum: 'user' or 'assistant'"),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Добавляем внешний ключ для chat_messages
    op.create_foreign_key(
        'fk_chat_messages_session_id',
        'chat_messages', 'chat_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Создаем индексы для chat_messages
    op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_timestamp'), 'chat_messages', ['timestamp'], unique=False)


def downgrade() -> None:
    # Удаляем таблицы и индексы в обратном порядке
    op.drop_index(op.f('ix_chat_messages_timestamp'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_session_id'), table_name='chat_messages')
    op.drop_constraint('fk_chat_messages_session_id', 'chat_messages', type_='foreignkey')
    op.drop_table('chat_messages')
    
    op.drop_index(op.f('ix_chat_sessions_user_id'), table_name='chat_sessions')
    op.drop_index(op.f('ix_chat_sessions_user_file_id'), table_name='chat_sessions')
    op.drop_constraint('fk_chat_sessions_user_id', 'chat_sessions', type_='foreignkey')
    op.drop_constraint('fk_chat_sessions_user_file_id', 'chat_sessions', type_='foreignkey')
    op.drop_table('chat_sessions')
    
    # Удаляем уникальный индекс
    conn = op.get_bind()
    conn.execute(sa.text("DROP INDEX IF EXISTS uq_user_files_id"))
