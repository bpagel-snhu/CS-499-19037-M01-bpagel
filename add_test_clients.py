#!/usr/bin/env python3
"""
Script to add test clients to the database for testing dropdown behavior with many clients.
"""

import random
import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_renamer.tools.database_logging.database_manager import DatabaseManager

# Lists of realistic names
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", 
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa", 
    "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna", 
    "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle", 
    "Kenneth", "Laura", "Kevin", "Emily", "Brian", "Kimberly", "George", "Deborah", 
    "Edward", "Dorothy", "Ronald", "Lisa", "Timothy", "Nancy", "Jason", "Karen", 
    "Jeffrey", "Betty", "Ryan", "Helen", "Jacob", "Sandra", "Gary", "Donna", 
    "Nicholas", "Carol", "Eric", "Ruth", "Jonathan", "Sharon", "Stephen", "Michelle", 
    "Larry", "Laura", "Justin", "Emily", "Scott", "Kimberly", "Brandon", "Deborah", 
    "Benjamin", "Dorothy", "Samuel", "Lisa", "Frank", "Nancy", "Gregory", "Karen", 
    "Raymond", "Betty", "Alexander", "Helen", "Patrick", "Sandra", "Jack", "Donna"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", 
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", 
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", 
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", 
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", 
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", 
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy", 
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey", 
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson", 
    "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes", 
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", 
    "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", 
    "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez", "Simmons"
]

def add_test_clients():
    """Add 50 random test clients to the database."""
    db_manager = DatabaseManager()
    
    print("Adding 50 test clients to the database...")
    
    added_count = 0
    skipped_count = 0
    
    for i in range(50):
        # Generate random name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Add some variety - some archived, some with middle initials
        is_active = random.choice([True, True, True, False])  # 75% active, 25% archived
        
        # Occasionally add a middle initial
        if random.random() < 0.3:  # 30% chance
            middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            first_name = f"{first_name} {middle_initial}."
        
        try:
            db_manager.add_client(first_name, last_name, is_active)
            status = " (Archived)" if not is_active else ""
            print(f"✓ Added: {last_name}, {first_name}{status}")
            added_count += 1
        except ValueError as e:
            # Client already exists (duplicate name)
            print(f"⚠ Skipped: {last_name}, {first_name} (already exists)")
            skipped_count += 1
    
    print(f"\nSummary:")
    print(f"  Added: {added_count} clients")
    print(f"  Skipped: {skipped_count} clients (duplicates)")
    print(f"  Total: {added_count + skipped_count} attempts")
    
    # Show current database stats
    try:
        all_clients = db_manager.get_clients(include_archived=True)
        active_clients = db_manager.get_clients(include_archived=False)
        print(f"\nDatabase stats:")
        print(f"  Total clients: {len(all_clients)}")
        print(f"  Active clients: {len(active_clients)}")
        print(f"  Archived clients: {len(all_clients) - len(active_clients)}")
    except Exception as e:
        print(f"Error getting database stats: {e}")

if __name__ == "__main__":
    add_test_clients() 