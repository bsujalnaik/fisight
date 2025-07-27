import React from 'react';
import { Button } from '@/components/ui/button';
import { useUser } from '@/contexts/UserContext';
import { markUserAsPro, removeProStatus } from '@/lib/firebase';
import { Crown, User } from 'lucide-react';

export const ProStatusToggle: React.FC = () => {
  const { user, isPro, loadingUser } = useUser();

  const handleTogglePro = async () => {
    if (!user) return;
    
    if (isPro) {
      await removeProStatus(user.uid);
    } else {
      await markUserAsPro(user.uid);
    }
  };

  if (loadingUser || !user) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Button
        onClick={handleTogglePro}
        variant={isPro ? "destructive" : "default"}
        className={`flex items-center gap-2 ${
          isPro 
            ? 'bg-amber-500 hover:bg-amber-600 text-white' 
            : 'bg-primary hover:bg-primary/90'
        }`}
        size="sm"
      >
        {isPro ? (
          <>
            <Crown className="w-4 h-4" />
            Remove Pro
          </>
        ) : (
          <>
            <User className="w-4 h-4" />
            Make Pro
          </>
        )}
      </Button>
    </div>
  );
}; 