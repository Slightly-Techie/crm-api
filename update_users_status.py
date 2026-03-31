"""Script to update all users' status from TO_CONTACT to ACCEPTED"""
from db.database import SessionLocal
from db.models.users import User
from utils.enums import UserStatus


def update_users_status():
    """Update all users' status from TO_CONTACT to ACCEPTED"""
    db = SessionLocal()
    
    try:
        # Get all users with TO_CONTACT status
        users_to_update = db.query(User).filter(
            User.status == UserStatus.TO_CONTACT
        ).all()
        
        print(f"Found {len(users_to_update)} users with TO_CONTACT status")
        
        if len(users_to_update) == 0:
            print("No users to update!")
            return
        
        # Update all to ACCEPTED status
        for user in users_to_update:
            user.status = UserStatus.ACCEPTED
            print(f"✓ Updated {user.email}: {user.status}")
        
        db.commit()
        print(f"\n✅ Successfully updated {len(users_to_update)} users to ACCEPTED status!")
        
        # Display the updated users
        updated_users = db.query(User).filter(
            User.status == UserStatus.ACCEPTED
        ).all()
        
        print(f"\nTotal users with ACCEPTED status: {len(updated_users)}")
        for user in updated_users:
            print(f"  - {user.email} ({user.first_name} {user.last_name}) - Status: {user.status}")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating users: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    update_users_status()
