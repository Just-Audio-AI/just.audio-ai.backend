"""Insert products based on PricingSection

Revision ID: 2024_08_insert_pricing_products
Revises: c2ae2431b1d0
Create Date: 2024-08-18

"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid4
import json
from datetime import datetime, timedelta

# revision identifiers, used by Alembic.
revision = '2024_08_insert_pricing_products'
down_revision = 'a1e3b2f4ac80'  # Укажите здесь ID предыдущей миграции или None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Используем существующую таблицу products
    connection = op.get_bind()
    
    # Проверяем существование продуктов по slug
    existing_products = connection.execute(
        sa.text("SELECT slug FROM products WHERE slug IN ('free', 'premium', 'premium-plus')")
    ).fetchall()
    existing_slugs = {row[0] for row in existing_products}

    # Данные из PricingSection
    products_data = [
        {
            'uuid': str(uuid4()),
            'display_name': 'Бесплатно',
            'slug': 'free',
            'price': 0.0,
            'price_with_discount': None,
            'discount_deadline': None,
            'minute_count': 60,  # 60 минут в месяц
            'discount': 0.0,
            'is_active': True,
            'sort_order': 1,
            'is_subs': False,
            'billing_cycle': None,  # навсегда
            'features': json.dumps([
                'До 60 минут записи в месяц',
                'Базовая расшифровка аудио',
                'Стандартное качество звука',
                'Экспорт в TXT формат',
                'Поддержка по email'
            ], ensure_ascii=False),
            'is_can_select_gpt_model': False,
            'cta_text': 'Попробовать бесплатно',
            'gpt_request_limit_one_file': 5,
            'vtt_file_ext_support': False,
            'srt_file_ext_support': False
        },
        {
            'uuid': str(uuid4()),
            'display_name': 'Премиум',
            'slug': 'premium',
            'price': 990.0,
            'price_with_discount': None,
            'discount_deadline': None,
            'minute_count': 600,  # 10 часов
            'discount': 0.0,
            'is_active': True,
            'sort_order': 2,
            'is_subs': True,
            'billing_cycle': 'month',
            'features': json.dumps([
                'До 10 часов записи в месяц',
                'Продвинутая расшифровка аудио',
                'Улучшенное качество звука',
                'Удаление шума и фоновых звуков',
                'Экспорт в PDF, DOCX, TXT',
                'ChatGPT-помощник',
                'Приоритетная поддержка'
            ], ensure_ascii=False),
            'is_can_select_gpt_model': False,
            'cta_text': 'Выбрать Premium',
            'gpt_request_limit_one_file': 15,
            'vtt_file_ext_support': True,
            'srt_file_ext_support': True
        },
        {
            'uuid': str(uuid4()),
            'display_name': 'Премиум+',
            'slug': 'premium-plus',
            'price': 2490.0,
            'price_with_discount': None,
            'discount_deadline': None,
            'minute_count': -1,  # безлимитное количество
            'discount': 0.0,
            'is_active': True,
            'sort_order': 3,
            'is_subs': True,
            'billing_cycle': 'month',
            'features': json.dumps([
                'Безлимитное количество записей',
                'Расширенная расшифровка аудио',
                'AI-обработка звука',
                'Удаление шума, вокала и мелодий',
                'Все форматы экспорта',
                'Продвинутый ChatGPT-ассистент',
                'Выделенный менеджер',
                'API доступ'
            ], ensure_ascii=False),
            'is_can_select_gpt_model': True,
            'cta_text': 'Выбрать Premium+',
            'gpt_request_limit_one_file': 50,
            'vtt_file_ext_support': True,
            'srt_file_ext_support': True
        }
    ]

    # Вставляем только те продукты, которых еще нет
    for product in products_data:
        if product['slug'] not in existing_slugs:
            connection.execute(
                sa.text("""
                    INSERT INTO products (
                        uuid, display_name, slug, price, price_with_discount,
                        discount_deadline, minute_count, discount, is_active,
                        sort_order, is_subs, billing_cycle, features,
                        is_can_select_gpt_model, cta_text, 
                        gpt_request_limit_one_file, vtt_file_ext_support,
                        srt_file_ext_support
                    ) VALUES (
                        :uuid, :display_name, :slug, :price, :price_with_discount,
                        :discount_deadline, :minute_count, :discount, :is_active,
                        :sort_order, :is_subs, :billing_cycle, :features,
                        :is_can_select_gpt_model, :cta_text,
                        :gpt_request_limit_one_file, :vtt_file_ext_support,
                        :srt_file_ext_support
                    )
                """),
                product
            )
        else:
            # Обновляем существующие продукты
            connection.execute(
                sa.text("""
                    UPDATE products SET
                        display_name = :display_name,
                        price = :price,
                        price_with_discount = :price_with_discount,
                        discount_deadline = :discount_deadline,
                        minute_count = :minute_count,
                        discount = :discount,
                        is_active = :is_active,
                        sort_order = :sort_order,
                        is_subs = :is_subs,
                        billing_cycle = :billing_cycle,
                        features = :features,
                        is_can_select_gpt_model = :is_can_select_gpt_model,
                        cta_text = :cta_text,
                        gpt_request_limit_one_file = :gpt_request_limit_one_file,
                        vtt_file_ext_support = :vtt_file_ext_support,
                        srt_file_ext_support = :srt_file_ext_support
                    WHERE slug = :slug
                """),
                product
            )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM products WHERE slug IN ('free', 'premium', 'premium-plus')")
    ) 