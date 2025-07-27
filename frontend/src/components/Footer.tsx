import React from "react";

interface FooterProps {
  onTabChange: (tab: string) => void;
}

const Footer: React.FC<FooterProps> = ({ onTabChange }) => (
  <footer className="w-full bg-zinc-950 border-t-2 border-t-transparent border-t-gradient-to-r from-indigo-500 via-blue-400 to-green-400 py-10 px-4">
    <div className="w-full flex flex-col md:flex-row items-center md:items-start justify-between gap-8 md:gap-0 px-0 md:px-8">
      {/* Left: Logo and Description */}
      <div className="flex flex-col items-center md:items-start gap-2 md:w-1/3">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-400 flex items-center justify-center shadow-lg">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-trending-up w-6 h-6 text-white"
            >
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
              <polyline points="16 7 22 7 22 13"></polyline>
            </svg>
          </div>
          <span className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-green-400 bg-clip-text text-transparent drop-shadow">FinSight</span>
        </div>
        <p className="text-sm text-zinc-400 max-w-xs text-center md:text-left">
          Your AI-powered investment and tax optimization advisor. Secure, smart, and always available to help you grow your wealth.
        </p>
      </div>
      {/* Center: Navigation Links */}
      <nav className="flex flex-wrap justify-center gap-6 md:gap-8 text-base md:w-1/3">
        <button onClick={() => onTabChange('home')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">Home</button>
        <button onClick={() => onTabChange('dashboard')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">Dashboard</button>
        <button onClick={() => onTabChange('portfolio')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">Portfolio</button>
        <button onClick={() => onTabChange('chat')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">AI Chat</button>
        <button onClick={() => onTabChange('notifications')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">Alerts</button>
        <button onClick={() => onTabChange('settings')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">Settings</button>
        <button onClick={() => onTabChange('about')} className="text-zinc-300 hover:text-indigo-400 transition font-medium">About Us</button>
      </nav>
      {/* Right: Credit */}
      <div className="flex flex-col items-center md:items-end gap-2 md:w-1/3">
        <span className="text-sm text-zinc-400">Made by the <span className="text-indigo-400 font-semibold">FinSight Team</span></span>
        <span className="text-xs text-zinc-500 mt-2">&copy; {new Date().getFullYear()} FinSight. All rights reserved.</span>
      </div>
    </div>
  </footer>
);

export default Footer; 