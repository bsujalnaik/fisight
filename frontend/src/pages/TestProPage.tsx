import React from 'react';
import { useUser } from '@/contexts/UserContext';
import { Button } from '@/components/ui/button';
import { markUserAsPro, removeProStatus } from '@/lib/firebase';
import { Crown, User, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const TestProPage: React.FC = () => {
  const { user, isPro, loadingUser } = useUser();
  const navigate = useNavigate();

  const handleTogglePro = async () => {
    if (!user) return;
    
    if (isPro) {
      await removeProStatus(user.uid);
    } else {
      await markUserAsPro(user.uid);
    }
  };

  const handleGoToChat = () => {
    navigate('/chat');
  };

  if (loadingUser) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please Sign In</h1>
          <p className="text-muted-foreground">You need to be signed in to test Pro functionality.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Pro Status Test Page</h1>
        
        <div className="space-y-6">
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Current Status</h2>
            <div className="flex items-center gap-3 mb-4">
              {isPro ? (
                <>
                  <Crown className="w-6 h-6 text-amber-500" />
                  <span className="text-lg font-medium">Pro User</span>
                  <span className="bg-amber-500 text-white px-2 py-1 rounded text-sm">ACTIVE</span>
                </>
              ) : (
                <>
                  <User className="w-6 h-6 text-muted-foreground" />
                  <span className="text-lg font-medium">Regular User</span>
                  <span className="bg-muted text-muted-foreground px-2 py-1 rounded text-sm">FREE</span>
                </>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              User ID: {user.uid}
            </p>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Test Actions</h2>
            <div className="space-y-4">
              <Button
                onClick={handleTogglePro}
                variant={isPro ? "destructive" : "default"}
                className={`w-full ${
                  isPro 
                    ? 'bg-amber-500 hover:bg-amber-600 text-white' 
                    : 'bg-primary hover:bg-primary/90'
                }`}
              >
                {isPro ? (
                  <>
                    <Crown className="w-4 h-4 mr-2" />
                    Remove Pro Status
                  </>
                ) : (
                  <>
                    <User className="w-4 h-4 mr-2" />
                    Make Pro User
                  </>
                )}
              </Button>

              <Button
                onClick={handleGoToChat}
                variant="outline"
                className="w-full"
              >
                <ArrowRight className="w-4 h-4 mr-2" />
                Go to Chat (Auto-routing)
              </Button>
            </div>
          </div>

          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Expected Behavior</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>• Pro users should automatically be redirected to /pro-ai-chat</li>
              <li>• Regular users should see the standard chat at /chat</li>
              <li>• Pro users cannot access regular chat (redirected)</li>
              <li>• Regular users cannot access Pro chat (redirected)</li>
              <li>• Status changes are reflected immediately</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}; 