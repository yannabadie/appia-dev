#!/usr/bin/env python3
"""
Explore existing Supabase dashboard setup and data
"""

import os

from supabase import create_client

# Setup Supabase client  # To be initialized
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # List all tables
    try:
        # Try to query logs table
        logs = supabase.table("logs").select("*").limit(5).execute()
        print("Logs table exists with data:", logs.data)
    except Exception as e:
        print("Logs table error:", e)

    # Try other common table names
    for table_name in ["tasks", "metrics", "dashboard", "jarvys_logs"]:
        try:
            result = supabase.table(table_name).select("*").limit(1).execute()
            print(f"{table_name} table exists")
        except:
            print(f"{table_name} table not found")
else:
    print("Supabase credentials not configured")
