import React from 'react';
import { useUser } from '@/contexts/UserContext';
import { AIChat } from './AIChat';
import { ProAIChat } from './ProAIChat';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

interface ChatRouterProps {
  forcePro?: boolean; // For testing purposes
}

export const ChatRouter: React.FC<ChatRouterProps> = ({ forcePro = false }) => {
  const { user, isPro, loadingUser } = useUser();
  const navigate = useNavigate();

  // Effect to handle automatic routing based on Pro status
  useEffect(() => {
    if (!loadingUser) {
      if (user && (isPro || forcePro)) {
        // User is Pro, ensure they're on the Pro route
        if (window.location.pathname !== '/pro-ai-chat') {
          navigate('/pro-ai-chat', { replace: true });
        }
      } else if (user && !isPro) {
        // User is not Pro, ensure they're on the regular chat route
        if (window.location.pathname === '/pro-ai-chat') {
          navigate('/chat', { replace: true });
        }
      }
    }
  }, [user, isPro, loadingUser, navigate, forcePro]);

  // Show loading while checking user status
  if (loadingUser) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted-foreground">Loading chat...</p>
        </div>
      </div>
    );
  }

  // If user is Pro (or forcePro is true), show Pro chat
  if (user && (isPro || forcePro)) {
    return <ProAIChat />;
  }

  // Otherwise, show regular chat
  return <AIChat />;
}; 