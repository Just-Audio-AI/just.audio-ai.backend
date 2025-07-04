"""init

Revision ID: d484a7f73c5d
Revises: 
Create Date: 2025-05-03 20:51:26.869721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd484a7f73c5d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False, comment="Название продукта, например '100 минут'"),
    sa.Column('slug', sa.String(), nullable=False, comment="Слаг продукта, например '100-minutes'"),
    sa.Column('price', sa.Float(), nullable=False, comment='Цена без скидки'),
    sa.Column('price_with_discount', sa.Float(), nullable=True, comment='Цена со скидкой'),
    sa.Column('discount_deadline', sa.DateTime(), nullable=True, comment='Срок действия скидки'),
    sa.Column('minute_count', sa.Integer(), nullable=False, comment='Количество минут'),
    sa.Column('discount', sa.Float(), nullable=False, comment='Процент скидки'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Активен ли продукт'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='Порядок сортировки'),
    sa.Column('is_subs', sa.Boolean(), nullable=False, comment='Подписка или разовая покупка'),
    sa.Column('billing_cycle', sa.String(), nullable=True, comment='Месяц, год'),
    sa.Column('features', sa.String(), nullable=True, comment="Список фич. Хранится как ['Фича 1', 'Фича 2']"),
    sa.Column('is_can_use_gpt', sa.Boolean(), nullable=False, comment='Поддерживается работа с GPT'),
    sa.Column('is_can_select_gpt_model', sa.Boolean(), nullable=False, comment='Может выбирать модель GPT'),
    sa.Column('cta_text', sa.String(), nullable=True, comment='Текст кнопки'),
    sa.Column('gpt_request_limit_one_file', sa.Integer(), nullable=True, comment='Лимит запросов в GPT по одному файлу'),
    sa.Column('vtt_file_ext_support', sa.Boolean(), nullable=False, comment='Поддерживается скачивание расшифровки в VTT формате'),
    sa.Column('srt_file_ext_support', sa.Boolean(), nullable=False, comment='Поддерживается скачивание расшифровки в SRT формате'),
    sa.Column('is_can_remove_melody', sa.Boolean(), nullable=False, comment='Поддерживается удаление мелодии'),
    sa.Column('is_can_remove_vocal', sa.Boolean(), nullable=False, comment='Поддерживается удаление голоса'),
    sa.Column('is_can_remove_noise', sa.Boolean(), nullable=False, comment='Поддерживается удаление шумов'),
    sa.Column('is_can_improve_audio', sa.Boolean(), nullable=False, comment='Поддерживается улучшение аудио'),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('user_email_with_code',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('firebase_token', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_files',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_url', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('external_id', sa.Uuid(), nullable=True),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('transcription', postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), nullable=True),
    sa.Column('transcription_text', sa.String(), nullable=True, comment='Транскрипция в формате plain text'),
    sa.Column('transcription_vtt', sa.String(), nullable=True, comment='Транскрипция в формате VTT'),
    sa.Column('transcription_srt', sa.String(), nullable=True, comment='Транскрипция в формате SRT'),
    sa.Column('duration', sa.Integer(), nullable=True, comment='Длительность файла в секундах'),
    sa.Column('file_size', sa.Integer(), nullable=True, comment='Размер файла в байтах'),
    sa.Column('mime_type', sa.String(), nullable=True, comment='MIME-тип файла'),
    sa.Column('removed_noise_file_url', sa.String(), nullable=True, comment='Ссылка на файл с удаленным шумом'),
    sa.Column('removed_noise_file_status', sa.String(), nullable=True, comment='Статус удаления шума'),
    sa.Column('removed_vocals_file_url', sa.String(), nullable=True, comment='Ссылка на файл с удаленным вокалом'),
    sa.Column('removed_vocal_file_status', sa.String(), nullable=True, comment='Статус удаления голоса'),
    sa.Column('removed_melody_file_url', sa.String(), nullable=True, comment='Ссылка на файл с удаленной мелодией'),
    sa.Column('removed_melody_file_status', sa.String(), nullable=True, comment='Статус удаления голоса'),
    sa.Column('improved_audio_file_url', sa.String(), nullable=True, comment='Ссылка на файл с улучшенным аудио'),
    sa.Column('improved_audio_file_status', sa.String(), nullable=True, comment='Статус улучшения аудио'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id', 'user_id')
    )
    op.create_table('user_products',
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('minute_count', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False, comment='Сумма оплаты'),
    sa.Column('expires_at', sa.DateTime(), nullable=True, comment='Дата окончания подписке'),
    sa.Column('is_subscription', sa.Boolean(), nullable=False, comment='Является ли записью подписки'),
    sa.Column('subscription_id', sa.String(), nullable=True, comment='ID подписки в CloudPayments'),
    sa.Column('interval', sa.String(), nullable=True, comment='Month или Year'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Активна ли подписка'),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.uuid'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('chat_sessions',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('user_file_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['user_file_id', 'user_id'],
                        ['user_files.id', 'user_files.user_id'],
                        ondelete='CASCADE'
                    ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    op.create_table('transactions',
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('external_transaction_id', sa.String(), nullable=True, comment='Id транзакции в CloudPayments'),
    sa.Column('status', sa.String(), nullable=False, comment='Статус транзакции'),
    sa.Column('metainfo', sa.JSON(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('user_product_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.uuid'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_product_id'], ['user_products.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    ),
    op.create_table('user_products_to_products',
    sa.Column('uuid', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('user_product', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.uuid'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_product'], ['user_products.uuid'], ),
    sa.PrimaryKeyConstraint('uuid')
    ),
    op.create_table('chat_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('sender', sa.String(), nullable=False, comment="Enum: 'user' or 'assistant'"),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    ),
    # Добавляем внешний ключ для chat_messages
    op.create_foreign_key(
        'fk_chat_messages_session_id',
        'chat_messages', 'chat_sessions',
        ['session_id'], ['id'],
        ondelete='CASCADE'
    )

    # Создаем индексы для chat_messages
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat_messages')
    op.drop_table('user_products_to_products')
    op.drop_table('transactions')
    op.drop_table('chat_sessions')
    op.drop_table('user_products')
    op.drop_table('user_files')
    op.drop_table('users')
    op.drop_table('user_email_with_code')
    op.drop_table('products')
    # ### end Alembic commands ###
