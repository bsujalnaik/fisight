// src/components/Layout.tsx
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Navigation } from '@/components/Navigation';
import Footer from '@/components/Footer';
import { useUser } from "@/contexts/UserContext"; // Assuming you need this for the chat link

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isPro } = useUser();

  // Determines the active tab from the URL
  const getActiveTab = (pathname: string): string => {
    if (pathname === '/') return 'home';
    if (pathname.startsWith('/dashboard')) return 'dashboard';
    if (pathname.startsWith('/chat') || pathname.startsWith('/pro-ai-chat')) return 'chat';
    if (pathname.startsWith('/portfolio')) return 'portfolio';
    if (pathname.startsWith('/alerts')) return 'notifications';
    if (pathname.startsWith('/settings')) return 'settings';
    if (pathname.startsWith('/about')) return 'about';
    return 'home';
  };

  const activeTab = getActiveTab(location.pathname);

  // Navigates to the correct URL when a tab is clicked
  const handleTabChange = (tabId: string) => {
    let path = '/';
    switch (tabId) {
      case 'home':
        path = '/';
        break;
      case 'dashboard':
        path = '/dashboard';
        break;
      case 'chat':
        path = isPro ? '/pro-ai-chat' : '/chat';
        break;
      case 'portfolio':
        path = '/portfolio';
        break;
      case 'notifications':
        path = '/alerts';
        break;
      case 'settings':
        path = '/settings';
        break;
      case 'about':
        path = '/about';
        break;
      default:
        path = '/';
    }
    navigate(path);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      {/* The Navigation component is rendered ONCE here */}
      <Navigation activeTab={activeTab} onTabChange={handleTabChange} />

      {/* The page content (e.g., <Dashboard />) is rendered here */}
      <main className="flex-grow w-full">
          {children}
      </main>

      {/* The Footer component is rendered ONCE here */}
      <Footer onTabChange={handleTabChange} />
    </div>
  );
};

export default Layout;
