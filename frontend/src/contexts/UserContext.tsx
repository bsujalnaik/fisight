// src/contexts/UserContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, db } from '@/lib/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { doc, onSnapshot, setDoc, serverTimestamp } from 'firebase/firestore';

interface UserContextType {
  user: any; // FirebaseUser object
  isPro: boolean; // Indicates if the user has a pro subscription
  loadingUser: boolean; // Indicates if user authentication state is still loading
  markUserAsPro: (userId: string) => Promise<void>; // Function to mark user as Pro
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any>(null);
  const [isPro, setIsPro] = useState(false); // Default to false
  const [loadingUser, setLoadingUser] = useState(true); // Initially true

  // Function to mark a user as Pro (for testing purposes)
  const markUserAsPro = async (userId: string) => {
    try {
      const userDocRef = doc(db, "users", userId);
      await setDoc(userDocRef, {
        isPro: true,
        proUpgradedAt: serverTimestamp(),
      }, { merge: true });
      console.log('User marked as Pro successfully');
    } catch (error) {
      console.error('Error marking user as Pro:', error);
    }
  };

  useEffect(() => {
    const unsubscribeAuth = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setLoadingUser(false); // Auth state loaded

      if (firebaseUser) {
        // If user is logged in, set up a real-time listener for their user document
        // This allows `isPro` to update automatically if changed in Firestore
        const userDocRef = doc(db, "users", firebaseUser.uid);
        const unsubscribeFirestore = onSnapshot(userDocRef, (docSnap) => {
          if (docSnap.exists()) {
            // Check for an 'isPro' field in the user's document
            const userData = docSnap.data();
            setIsPro(userData.isPro || false);
          } else {
            setIsPro(false); // User document doesn't exist or no pro status
          }
        }, (error) => {
          console.error('Error listening to user document:', error);
          setIsPro(false);
        });
        
        // Clean up the Firestore listener when component unmounts or user changes
        return () => unsubscribeFirestore();
      } else {
        // If no user is logged in, ensure isPro is false
        setIsPro(false);
      }
    });

    // Clean up the Auth state listener when component unmounts
    return () => unsubscribeAuth();
  }, []); // Empty dependency array means this effect runs once on mount

  return (
    <UserContext.Provider value={{ user, isPro, loadingUser, markUserAsPro }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
