#!/usr/bin/env python
"""
Safe migration script that handles existing tables gracefully.
This script checks if tables exist before running migrations.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def get_applied_migrations():
    """Get list of applied migrations from django_migrations table."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'sales' ORDER BY id;")
            return [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]
    except Exception:
        # Table doesn't exist yet
        return []

def main():
    """Run migrations safely, handling existing tables."""

    print("=" * 70)
    print("SAFE MIGRATION SCRIPT")
    print("=" * 70)

    # Check if critical tables exist
    critical_tables = [
        'sales_attribute',
        'sales_coupon',
        'sales_category',
        'sales_attributevalue',
        'sales_productvariant',
    ]

    existing_tables = [table for table in critical_tables if table_exists(table)]
    applied_migrations = get_applied_migrations()

    print(f"\nExisting tables found: {len(existing_tables)}")
    for table in existing_tables:
        print(f"  + {table}")

    print(f"\nApplied migrations: {len(applied_migrations)}")
    for migration in applied_migrations[-5:]:  # Show last 5
        print(f"  + {migration}")

    # Check if migration 0006 needs to be faked
    migration_0006_applied = any('0006_attribute_coupon' in m for m in applied_migrations)

    if existing_tables and not migration_0006_applied:
        print("\n" + "!" * 70)
        print("WARNING: Tables exist but migration 0006 not applied!")
        print("This likely means tables were created manually or by a previous deploy.")
        print("Marking migration 0006 as applied (direct SQL insert)...")
        print("!" * 70 + "\n")

        # Insert migration record directly into django_migrations table
        try:
            with connection.cursor() as cursor:
                # First check if it already exists (double check)
                cursor.execute("""
                    SELECT COUNT(*) FROM django_migrations
                    WHERE app = 'sales' AND name = '0006_attribute_coupon_remove_product_color_and_more';
                """)
                exists = cursor.fetchone()[0] > 0

                if not exists:
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied)
                        VALUES ('sales', '0006_attribute_coupon_remove_product_color_and_more', NOW());
                    """)
                    print("[OK] Migration 0006 marked as applied (inserted into django_migrations)")
                else:
                    print("[INFO] Migration 0006 already exists in django_migrations")
        except Exception as e:
            print(f"[ERROR] Could not insert migration 0006 record: {e}")
            print("This may cause the migration to fail. Consider manual intervention.")
            # Don't exit, let the normal migration attempt to run

    # Run normal migrations
    print("\n" + "=" * 70)
    print("Running migrations...")
    print("=" * 70 + "\n")

    try:
        execute_from_command_line([
            'manage.py',
            'migrate',
            '--no-input',
            '--fake-initial'
        ])
        print("\n[SUCCESS] Migrations completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
