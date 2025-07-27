// src/App.tsx (Final Correct Version)
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Import your Layout
import Layout from './components/Layout';

// Import your pages
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import SubscriptionPlansPage from "./pages/SubscriptionPlansPage";
import PaymentPage from "./pages/PaymentPage";
import { ProAIChat } from './components/ProAIChat';
import { AIChat } from './components/AIChat';
import { ChatRouter } from './components/ChatRouter';
import { ProStatusToggle } from './components/ProStatusToggle';
import { TestProPage } from './pages/TestProPage';
import MyStocks from "./components/MyStocks";

// Import your contexts
import { UserProvider } from "@/contexts/UserContext";
import { PortfolioProvider } from './contexts/PortfolioContext';
import PortfolioOverview from "./components/PortfolioOverview";
import Dashboard from "./components/Dashboard";
import AlertsPage from "./pages/alerts";
import Settings from "./components/Settings";
import AboutPage from "./pages/AboutPage";
import { useUser } from './contexts/UserContext';
import { AuthPage } from './pages/AuthPage';

const queryClient = new QueryClient();

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loadingUser } = useUser();
  
  if (loadingUser) {
    return (
      <Layout>
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }
  
  if (!user) {
    return <Layout><AuthPage /></Layout>;
  }
  
  return <>{children}</>;
};

// Pro Route Component - Only accessible to Pro users
const ProRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isPro, loadingUser } = useUser();
  
  if (loadingUser) {
    return (
      <Layout>
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }
  
  if (!user) {
    return <Navigate to="/" replace />;
  }
  
  if (!isPro) {
    return <Navigate to="/chat" replace />;
  }
  
  return <>{children}</>;
};

const PortfolioRoute = () => {
  return (
    <ProtectedRoute>
      <Layout><PortfolioOverview /></Layout>
    </ProtectedRoute>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <UserProvider>
        <PortfolioProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
              
              {/* Chat Routes with Automatic Pro Detection */}
              <Route path="/chat" element={<Layout><ChatRouter /></Layout>} />
              <Route path="/pro-ai-chat" element={
                <ProRoute>
                  <Layout><ProAIChat /></Layout>
                </ProRoute>
              } />
              
              <Route path="/portfolio" element={<PortfolioRoute />} />
              <Route path="/alerts" element={<Layout><AlertsPage /></Layout>} />
              <Route path="/settings" element={<Layout><Settings /></Layout>} />
              <Route path="/about" element={<Layout><AboutPage /></Layout>} />

              {/* --- Standalone pages that DON'T need the layout --- */}
              <Route path="/pro-subscription" element={<SubscriptionPlansPage />} />
              <Route path="/payment" element={<PaymentPage />} />
              <Route path="/test-pro" element={<TestProPage />} />

              {/* Always keep the catch-all "*" route at the very end */}
              <Route path="*" element={<NotFound />} />
            </Routes>
            
            {/* Test component for toggling Pro status - remove in production */}
            <ProStatusToggle />
          </BrowserRouter>
        </PortfolioProvider>
      </UserProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;