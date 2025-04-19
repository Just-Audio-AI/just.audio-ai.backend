"""Insert base products

Revision ID: 2024_03_20_insert_base_products
Revises: 
Create Date: 2024-03-20

"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = '2024_03_20_insert_base_products'
down_revision = "e31b3f5c0d39"  # Укажите здесь ID предыдущей миграции
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Используем существующую таблицу products
    connection = op.get_bind()
    
    # Проверяем существование продуктов по slug
    existing_products = connection.execute(
        sa.text("SELECT slug FROM products WHERE slug IN ('basic', 'standard', 'premium')")
    ).fetchall()
    existing_slugs = {row[0] for row in existing_products}

    # Базовые продукты для вставки
    products_data = [
        {
            'uuid': str(uuid4()),
            'display_name': 'Базовый',
            'slug': 'basic',
            'price': 299.0,
            'price_with_discount': None,
            'discount_deadline': None,
            'minute_count': 60,
            'discount': 0.0
        },
        {
            'uuid': str(uuid4()),
            'display_name': 'Стандарт',
            'slug': 'standard',
            'price': 699.0,
            'price_with_discount': None,
            'discount_deadline': None,
            'minute_count': 180,
            'discount': 0.0
        },
        {
            'uuid': str(uuid4()),
            'display_name': 'Премиум',
            'slug': 'premium',
            'price': 1299.0,
            'price_with_discount': None,
            'discount_deadline': None,
            'minute_count': 360,
            'discount': 0.0
        }
    ]

    # Вставляем только те продукты, которых еще нет
    for product in products_data:
        if product['slug'] not in existing_slugs:
            connection.execute(
                sa.text("""
                    INSERT INTO products (
                        uuid, display_name, slug, price, price_with_discount,
                        discount_deadline, minute_count, discount
                    ) VALUES (
                        :uuid, :display_name, :slug, :price, :price_with_discount,
                        :discount_deadline, :minute_count, :discount
                    )
                """),
                product
            )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM products WHERE slug IN ('basic', 'standard', 'premium')")
    )
