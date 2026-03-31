"""Script to update all users' role_id to 2"""
from db.database import SessionLocal
from db.models.users import User
from db.models.roles import Role


def update_users_role():
    """Update all users' role_id to 2"""
    db = SessionLocal()
    
    try:
        # First, check what role_id 2 is
        role_2 = db.query(Role).filter(Role.id == 2).first()
        if role_2:
            print(f"Role ID 2 is: {role_2.name}")
        else:
            print("Role ID 2 not found!")
            return
        
        # Get all users
        all_users = db.query(User).all()
        print(f"\nFound {len(all_users)} users to update")
        
        if len(all_users) == 0:
            print("No users to update!")
            return
        
        # Update all users to role_id 2
        for user in all_users:
            old_role_id = user.role_id
            user.role_id = 2
            print(f"✓ Updated {user.email}: role_id {old_role_id} → 2")
        
        db.commit()
        print(f"\n✅ Successfully updated {len(all_users)} users to role_id 2!")
        
        # Display the updated users
        updated_users = db.query(User).all()
        
        print(f"\nTotal users updated: {len(updated_users)}")
        print(f"All users now have role_id: 2 ({role_2.name})")
        for user in updated_users[:5]:
            print(f"  - {user.email} - role_id: {user.role_id}")
        if len(updated_users) > 5:
            print(f"  ... and {len(updated_users) - 5} more")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating users: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    update_users_role()
