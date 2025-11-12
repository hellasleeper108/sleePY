"""
Game Simulation Test Script

Test the RPG mechanics by simulating user progression

Usage:
    python test_game_simulation.py
"""
from app.db.session import SessionLocal, init_db
from app.services.game_engine import GameSimulator


def main():
    """Run game simulations"""
    print("\n" + "=" * 70)
    print("PyQuest RPG Mechanics Test Simulation")
    print("=" * 70)

    # Initialize database
    print("\nInitializing database...")
    init_db()

    db = SessionLocal()

    try:
        # Test 1: Simulate 7 days of progression
        print("\n\n" + "🎮" * 35)
        print("TEST 1: SIMULATING 7-DAY PROGRESSION")
        print("🎮" * 35)

        GameSimulator.simulate_user_progression(
            db=db,
            username="simulator_1",
            days=7,
            challenges_per_day=3
        )

        # Test 2: Test loot system
        print("\n\n" + "🎲" * 35)
        print("TEST 2: LOOT SYSTEM TEST (20 CHESTS)")
        print("🎲" * 35)

        GameSimulator.test_loot_system(
            db=db,
            username="simulator_1",
            num_chests=20
        )

        # Test 3: Longer simulation with more challenges
        print("\n\n" + "⚡" * 35)
        print("TEST 3: INTENSE 14-DAY PROGRESSION (5 CHALLENGES/DAY)")
        print("⚡" * 35)

        GameSimulator.simulate_user_progression(
            db=db,
            username="power_user",
            days=14,
            challenges_per_day=5
        )

        print("\n\n" + "=" * 70)
        print("✅ ALL SIMULATIONS COMPLETE!")
        print("=" * 70)

        print("\n📝 Summary:")
        print("   • Tested XP and leveling system")
        print("   • Tested daily streak mechanics")
        print("   • Tested loot chest generation and opening")
        print("   • Tested achievement unlocking")
        print("   • Tested milestone rewards")

        print("\n💡 Next Steps:")
        print("   1. Check the database to see created users and data")
        print("   2. Start the server: uvicorn main:app --reload")
        print("   3. Test the API endpoints at http://localhost:8000/docs")
        print("   4. Log in as 'simulator_1' or 'power_user' (password: test123)")

    finally:
        db.close()


if __name__ == "__main__":
    main()
