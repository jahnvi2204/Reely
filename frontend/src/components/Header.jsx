// Header component with user info and logout
import React from 'react';
import { signOutUser } from '../services/firebase';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, User, Video } from 'lucide-react';
import toast from 'react-hot-toast';

const Header = () => {
  const { user } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOutUser();
      toast.success('Successfully signed out');
    } catch (error) {
      console.error('Sign out error:', error);
      toast.error('Failed to sign out');
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Video className="w-8 h-8 text-indigo-600 mr-3" />
            <h1 className="text-xl font-bold text-gray-900">Reely</h1>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <User className="w-5 h-5 text-gray-500" />
              <span className="text-sm text-gray-700">
                {user?.displayName || user?.email}
              </span>
            </div>
            
            <button
              onClick={handleSignOut}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
