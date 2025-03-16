from typing import List, Set


class UserService:
    """Service for managing tracked users and checking if a user should be tracked."""
    
    def __init__(self, tracked_users: List[int]):
        """
        Initialize the UserService with a list of tracked users.
        
        Args:
            tracked_users: List of user IDs to track
        """
        self._tracked_users: Set[int] = set(tracked_users)
    
    def is_tracked(self, user_id: int) -> bool:
        """
        Check if a user is in the tracked users list.
        
        Args:
            user_id: The user ID to check
            
        Returns:
            True if the user should be tracked, False otherwise
        """
        return user_id in self._tracked_users
    
    def add_tracked_user(self, user_id: int) -> None:
        """
        Add a user to the tracked users list.
        
        Args:
            user_id: The user ID to add
        """
        self._tracked_users.add(user_id)
    
    def remove_tracked_user(self, user_id: int) -> None:
        """
        Remove a user from the tracked users list.
        
        Args:
            user_id: The user ID to remove
        """
        if user_id in self._tracked_users:
            self._tracked_users.remove(user_id)
    
    @property
    def tracked_users(self) -> List[int]:
        """
        Get the list of tracked users.
        
        Returns:
            List of tracked user IDs
        """
        return list(self._tracked_users) 